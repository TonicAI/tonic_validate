from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import copy
from typing import Callable, DefaultDict, List, Dict, Union
from tonic_validate.classes.benchmark import Benchmark, BenchmarkItem
import logging
from tonic_validate.classes.exceptions import LLMException

from tonic_validate.classes.llm_response import CallbackLLMResponse, LLMResponse
from tonic_validate.classes.run import Run, RunData
from tonic_validate.metrics.answer_consistency_metric import AnswerConsistencyMetric
from tonic_validate.metrics.answer_similarity_metric import AnswerSimilarityMetric
from tonic_validate.metrics.augmentation_precision_metric import (
    AugmentationPrecisionMetric,
)

from tonic_validate.metrics.metric import Metric
from tonic_validate.services.openai_service import OpenAIService
import tiktoken
from tonic_validate.utils.telemetry import Telemetry
from tqdm import tqdm
import time

logger = logging.getLogger()


class ValidateScorer:
    def __init__(
        self,
        metrics: List[Metric] = [
            AnswerSimilarityMetric(),
            AugmentationPrecisionMetric(),
            AnswerConsistencyMetric(),
        ],
        model_evaluator: str = "gpt-4-turbo-preview",
        max_parsing_retries: int = 3,
        max_llm_retries: int = 12,
        fail_on_error: bool = False,
        quiet: bool = False,
    ):
        """
        Create a Tonic Validate scorer.

        Parameters
        ----------
        metrics: List[Metric]
            The list of metrics to be used for scoring.
        model_evaluator: str
            The model to be used for scoring.
        max_parsing_retries: int
            The number of times to retry a failed score if it failed due to parsing.
        max_llm_retries: int
            The number of times to retry a failed llm request.
        fail_on_error: bool
            If True, an error in calculating a metric will raise an exception. If False, the score will be set to None.
        quiet: bool
            If True, will suppress all logging except errors.
        """
        self.metrics = metrics
        self.model_evaluator = model_evaluator
        self.max_parsing_retries = max_parsing_retries
        self.max_llm_retries = max_llm_retries
        self.fail_on_error = fail_on_error
        logger.setLevel(logging.ERROR if quiet else logging.INFO)
        self.quiet = quiet
        self.telemetry = Telemetry()
        try:
            self.encoder = tiktoken.encoding_for_model(model_evaluator)
        except Exception as _:
            logger.info("Defaulting to cl100k_base for measuring token count")
            self.encoder = tiktoken.get_encoding("cl100k_base")

    def _score_item_rundata(self, response: LLMResponse) -> RunData:
        """
        Calculates scores for a single LLMResponse object

        Parameters
        ----------
        response: LLMResponse
            The LLMResponse object to calculate scores for

        Returns
        -------
        RunData
            Contains the scores and other data
        """
        scores: Dict[str, Union[float, None]] = {}
        # We cache per response, so we need to create a new OpenAIService
        openai_service = OpenAIService(
            self.encoder, self.model_evaluator, max_retries=self.max_llm_retries
        )
        for metric in self.metrics:
            tries = 0
            exceptions = []
            last_cache = copy.deepcopy(openai_service.cache)
            while tries < self.max_parsing_retries:
                try:
                    scores[metric.name] = metric.score(response, openai_service)
                    break
                except LLMException as e:
                    if self.fail_on_error:
                        raise Exception("Error getting LLM response: " + str(e))
                    scores[metric.name] = None
                    logger.warning(
                        f"Error getting LLM response. Setting score to None. {e}"
                    )
                    # We reset the cache since we failed and don't want a failing cache to be used on the next metric
                    openai_service.cache = last_cache
                    break
                except Exception as e:
                    tries += 1
                    openai_service.cache = last_cache
                    logger.warning(f"Error calculating {metric.name}: {e}. Retrying...")
                    exceptions.append(e)

            if tries == self.max_parsing_retries:
                if self.fail_on_error:
                    raise Exception(
                        f"Error calculating metric {metric.name}: " + str(exceptions)
                    )
                scores[metric.name] = None
                logger.warning(
                    f"Error calculating {metric.name}. Setting score to None."
                )
                # We reset the cache since we failed and don't want a failing cache to be used on the next metric
                openai_service.cache = last_cache
        benchmark_item = response.benchmark_item
        return RunData(
            scores,
            benchmark_item.question,
            benchmark_item.answer,
            response.llm_answer,
            response.llm_context_list,
        )

    def score_responses(
        self, responses: List[LLMResponse], parallelism: int = 1
    ) -> Run:
        """Calculate metric scores for a list of LLMResponse objects.

        Parameters
        ----------
        responses: List[LLMResponse]
            The list of LLMResponse objects to be scored.
        parallelism: int
            The number of threads to use for scoring.

        Returns
        -------
        Run
            The Run object containing the scores and other data.
        """
        try:
            self.telemetry.log_run(
                len(responses), [metric.name for metric in self.metrics]
            )
        except Exception as _:
            pass

        run_data: List[RunData] = []

        with ThreadPoolExecutor(max_workers=parallelism) as executor:
            run_data = list(
                tqdm(
                    executor.map(self._score_item_rundata, responses),
                    total=len(responses),
                    desc="Scoring responses",
                    disable=self.quiet,
                )
            )

        # Used to calculate overall score
        total_scores: DefaultDict[str, float] = defaultdict(float)
        num_scores: DefaultDict[str, int] = defaultdict(int)

        for item in run_data:
            for metric_name, score in item.scores.items():
                if score is not None:
                    total_scores[metric_name] += score
                    num_scores[metric_name] += 1

        overall_scores: Dict[str, float] = {
            metric: total / num_scores[metric] for metric, total in total_scores.items()
        }

        return Run(overall_scores, run_data, None)

    # TODO: For backwards compatibility, remove in the future
    def score_run(self, responses: List[LLMResponse], parallelism: int = 1) -> Run:
        """
        Alias for score_responses. Used for backward compatibility
        """
        return self.score_responses(responses, parallelism)

    def score(
        self,
        benchmark: Benchmark,
        callback: Callable[[str], CallbackLLMResponse],
        callback_parallelism=1,
        scoring_parallelism=1,
    ) -> Run:
        """Calculate metric scores for a benchmark.

        Parameters
        ----------
        benchmark: Benchmark
            The benchmark to be scored. Can either be a Benchmark object or a list of BenchmarkItem objects.
        callback: Callable[[str], CallbackLLMResponse]
            A callback function that takes a question and returns a tuple of the llm response and the retrieved context list.
        callback_parallelism: int
            The number of threads to use for the callback function.
        scoring_parallelism: int
            The number of threads to use for scoring.

        Returns
        -------
        Run
            The Run object containing the scores and other data.
        """
        responses: List[LLMResponse] = []

        def create_response(item: BenchmarkItem) -> LLMResponse:
            # Time the callback
            start_time = time.time()
            callback_response = callback(item.question)
            end_time = time.time()
            run_time = end_time - start_time
            callback_response = callback(item.question)
            return LLMResponse(
                callback_response["llm_answer"],
                callback_response["llm_context_list"],
                item,
                run_time,
            )

        with ThreadPoolExecutor(max_workers=callback_parallelism) as executor:
            responses = list(
                tqdm(
                    executor.map(create_response, benchmark.items),
                    total=len(benchmark.items),
                    desc="Retrieving responses",
                    disable=self.quiet,
                )
            )

        return self.score_responses(responses, scoring_parallelism)
