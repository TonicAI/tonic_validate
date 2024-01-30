from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import DefaultDict, List

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.classes.run import Run, RunData
from tonic_validate.metrics.answer_similarity_metric import AnswerSimilarityMetric

from tonic_validate.metrics.metric import Metric
from tonic_validate.services.openai_service import OpenAIService


class ValidateScorer:
    def __init__(
        self, metrics: List[Metric], model_evaluator: str = "gpt-4-turbo-preview"
    ):
        self.metrics = metrics
        self.model_evaluator = model_evaluator

    def _score_item_rundata(self, response: LLMResponse) -> RunData:
        scores: dict[str, float] = {}
        # We cache per response, so we need to create a new OpenAIService
        openai_service = OpenAIService(self.model_evaluator)
        for metric in self.metrics:
            score = metric.score(response, openai_service)
            scores[metric.name] = score

        benchmark_item = response.benchmark_item
        return RunData(
            scores,
            benchmark_item.question,
            benchmark_item.answer,
            response.llm_answer,
            response.llm_context_list,
        )

    def score_run(self, responses: List[LLMResponse], parallelism=1) -> Run:
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
        run_data: list[RunData] = []

        with ThreadPoolExecutor(max_workers=parallelism) as executor:
            run_data = list(executor.map(self._score_item_rundata, responses))
        

        # Used to calculate overall score
        total_scores: DefaultDict[str, float] = defaultdict(float)
        num_scores: DefaultDict[str, int] = defaultdict(int)

        for item in run_data:
            for metric_name, score in item.scores.items():
                total_scores[metric_name] += score
                num_scores[metric_name] += 1
        
        overall_scores: dict[str, float] = {
            metric: total / num_scores[metric] for metric, total in total_scores.items()
        }
        
        return Run(overall_scores, run_data, None)