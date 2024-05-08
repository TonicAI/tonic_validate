from asyncio import Semaphore
import asyncio
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Awaitable, Callable, DefaultDict, List, Dict, Type, Union

from pydantic import ConfigDict, TypeAdapter, validate_call
from tonic_validate.classes.benchmark import Benchmark, BenchmarkItem
import logging
from tonic_validate.classes.exceptions import LLMException

from tonic_validate.classes.llm_response import CallbackLLMResponse, LLMResponse
from tonic_validate.classes.run import Run, RunData
import tonic_validate.metrics as tonic_metrics
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.services.litellm_service import LiteLLMService
import tiktoken
from tonic_validate.utils.telemetry import Telemetry
from tqdm.asyncio import tqdm as async_tqdm
from tqdm import tqdm
import time

logger = logging.getLogger()
CallbackValidator = TypeAdapter(CallbackLLMResponse)

# Gets a list of all the metric names
metric_dict: Dict[str, Type[tonic_metrics.Metric]] = {}
for metric in tonic_metrics.__all__:
    cls = getattr(tonic_metrics, metric)
    if not issubclass(cls, tonic_metrics.Metric):
        continue
    try:
        metric_dict[cls.__name__] = cls
    except AttributeError:
        print(f"The Metric {metric} does not have a '__name__' attribute.")


class ValidateScorer:
    DEFAULT_PARALLELISM_CALLBACK = 1
    DEFAULT_PARALLELISM_SCORING = 50

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(
        self,
        metrics: List[tonic_metrics.Metric] = [
            tonic_metrics.AnswerSimilarityMetric(),
            tonic_metrics.AugmentationPrecisionMetric(),
            tonic_metrics.AnswerConsistencyMetric(),
        ],
        model_evaluator: str = "gpt-4-turbo-preview",
        max_parsing_retries: int = 3,
        max_llm_retries: int = 10,
        fail_on_error: bool = False,
        quiet: bool = False,
    ):
        """
        Create a Tonic Validate scorer that can work with either OpenAIService or LiteLLMService.

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
        self.quiet = quiet
        self.telemetry = Telemetry()
        logger.setLevel(logging.ERROR if quiet else logging.INFO)

        try:
            self.encoder = tiktoken.encoding_for_model(model_evaluator)
        except Exception as _:
            logger.info("Defaulting to cl100k_base for measuring token count")
            self.encoder = tiktoken.get_encoding("cl100k_base")

        model_name_lower = self.model_evaluator.lower()
        if model_name_lower.startswith("gemini/") or model_name_lower.startswith(
            "claude"
        ):
            self.llm_service = LiteLLMService(
                self.encoder, self.model_evaluator, max_retries=self.max_llm_retries
            )
        else:
            self.llm_service = OpenAIService(
                self.encoder, self.model_evaluator, max_retries=self.max_llm_retries
            )

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    async def _score_item_rundata(
        self, response: LLMResponse, semaphore: Semaphore
    ) -> RunData:
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
        async with semaphore:
            scores: Dict[str, Union[float, None]] = {}
            for metric in self.metrics:
                tries = 0
                exceptions = []
                while tries < self.max_parsing_retries:
                    try:
                        scores[metric.name] = await metric.score(
                            response, self.llm_service
                        )
                        break
                    except LLMException as e:
                        if self.fail_on_error:
                            raise Exception("Error getting LLM response: " + str(e))
                        scores[metric.name] = None
                        logger.warning(
                            f"Error getting LLM response. Setting score to None. {e}"
                        )
                        break
                    except Exception as e:
                        tries += 1
                        logger.warning(
                            f"Error calculating {metric.name}: {e}. Retrying..."
                        )
                        exceptions.append(e)

                if tries == self.max_parsing_retries:
                    if self.fail_on_error:
                        raise Exception(
                            f"Error calculating metric {metric.name}: "
                            + str(exceptions)
                        )
                    scores[metric.name] = None
                    logger.warning(
                        f"Error calculating {metric.name}. Setting score to None."
                    )
            benchmark_item = response.benchmark_item
            return RunData(
                scores=scores,
                reference_question=benchmark_item.question,
                reference_answer=benchmark_item.answer,
                llm_answer=response.llm_answer,
                llm_context=response.llm_context_list,
            )

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    async def a_score_responses(
        self,
        responses: List[LLMResponse],
        parallelism: int = DEFAULT_PARALLELISM_SCORING,
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
            start_time = time.time()
        except Exception as _:
            start_time = -1

        semaphore = Semaphore(parallelism)
        tasks = [
            self._score_item_rundata(response, semaphore) for response in responses
        ]

        run_data: List[RunData] = await async_tqdm.gather(
            *tasks,
            total=len(tasks),
            desc="Scoring responses",
            disable=self.quiet,
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
        try:
            end_time = time.time()
            run_time = end_time - start_time
        except Exception as _:
            run_time = -1

        try:
            self.telemetry.log_run(
                len(responses), [metric.name for metric in self.metrics], run_time
            )
        except Exception as _:
            pass

        return Run(
            overall_scores=overall_scores,
            run_data=run_data,
            llm_evaluator=self.model_evaluator,
            id=None,
        )

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def score_responses(
        self,
        responses: List[LLMResponse],
        parallelism: int = DEFAULT_PARALLELISM_SCORING,
    ) -> Run:
        try:
            asyncio.get_running_loop()
            in_loop = True
        except RuntimeError:
            in_loop = False

        if in_loop:
            # Hack to get asyncio.run to work inside juptyer notebooks
            with ThreadPoolExecutor(1) as executor:
                return executor.submit(
                    asyncio.run, self.a_score_responses(responses, parallelism)
                ).result()
        else:
            return asyncio.run(self.a_score_responses(responses, parallelism))

    # TODO: For backwards compatibility, remove in the future
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def score_run(
        self,
        responses: List[LLMResponse],
        parallelism: int = DEFAULT_PARALLELISM_SCORING,
    ) -> Run:
        """
        Alias for score_responses. Used for backward compatibility
        """
        return self.score_responses(responses, parallelism)

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    async def a_score(
        self,
        benchmark: Benchmark,
        callback: Callable[[str], Awaitable[CallbackLLMResponse]],
        callback_parallelism=DEFAULT_PARALLELISM_CALLBACK,
        scoring_parallelism=DEFAULT_PARALLELISM_SCORING,
    ) -> Run:
        """Calculate metric scores for a benchmark asynchronously.

        Parameters
        ----------
        benchmark: Benchmark
            The benchmark to be scored. Can either be a Benchmark object or a list of BenchmarkItem objects.
        callback: Callable[[str], Awaitable[CallbackLLMResponse]]
            An async callback function that takes a question and returns a tuple of the llm response and the retrieved context list.
        callback_parallelism: int
            The number of threads to use for the callback function.
        scoring_parallelism: int
            The number of threads to use for scoring.

        Returns
        -------
        Run
            The Run object containing the scores and other data.
        """

        semaphore = Semaphore(callback_parallelism)

        async def create_response(item: BenchmarkItem) -> LLMResponse:
            async with semaphore:
                # Time the callback
                start_time = time.time()
                callback_response = await callback(item.question)
                CallbackValidator.validate_python(callback_response)
                end_time = time.time()
                run_time = end_time - start_time
                return LLMResponse(
                    llm_answer=callback_response["llm_answer"],
                    llm_context_list=callback_response["llm_context_list"],
                    benchmark_item=item,
                    run_time=run_time,
                )

        tasks = [create_response(item) for item in benchmark.items]
        responses: List[LLMResponse] = await async_tqdm.gather(
            *tasks,
            total=len(tasks),
            desc="Retrieving responses",
            disable=self.quiet,
        )

        return await self.a_score_responses(responses, scoring_parallelism)

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def score(
        self,
        benchmark: Benchmark,
        callback: Callable[[str], CallbackLLMResponse],
        callback_parallelism=DEFAULT_PARALLELISM_CALLBACK,
        scoring_parallelism=DEFAULT_PARALLELISM_SCORING,
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
            # Validate type of callback_response
            CallbackValidator.validate_python(callback_response)
            end_time = time.time()
            run_time = end_time - start_time
            return LLMResponse(
                llm_answer=callback_response["llm_answer"],
                llm_context_list=callback_response["llm_context_list"],
                benchmark_item=item,
                run_time=run_time,
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

    @staticmethod
    def metric_config_to_list(config: Dict[str, Dict[str, Any]]):
        metrics: List[tonic_metrics.Metric] = []
        for metric in config:
            if metric not in metric_dict:
                raise Exception(f"Metric {metric} not found.")
            metrics.append(metric_dict[metric].from_config(config[metric]))
        return metrics
