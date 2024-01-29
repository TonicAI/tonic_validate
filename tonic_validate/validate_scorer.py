from typing import List

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.classes.run import Run, RunData

from tonic_validate.metrics.metric import Metric
from tonic_validate.services.openai_service import OpenAIService


class ValidateScorer:
    def __init__(
        self, metrics: List[Metric], model_evaluator: str = "gpt-4-turbo-preview"
    ):
        self.metrics = metrics
        self.model_evaluator = model_evaluator

    def score_run(self, responses: List[LLMResponse]) -> Run:
        """Calculate metric scores for a list of LLMResponse objects.

        Parameters
        ----------
        responses: List[LLMResponse]
            The list of LLMResponse objects to be scored.

        Returns
        -------
        Run
            The Run object containing the scores and other data.
        """
        run_data: list[RunData] = []
        total_scores: dict[str, float] = {}
        score_counts: dict[str, int] = {}
        for response in responses:
            scores: dict[str, float] = {}
            # We cache per response, so we need to create a new OpenAIService
            openai_service = OpenAIService(self.model_evaluator)
            for metric in self.metrics:
                score = metric.score(response, openai_service)
                scores[metric.name] = score
                if metric.name not in total_scores:
                    total_scores[metric.name] = 0
                total_scores[metric.name] += score
                if metric.name not in score_counts:
                    score_counts[metric.name] = 0
                score_counts[metric.name] += 1

            benchmark_item = response.benchmark_item
            run_data.append(
                RunData(
                    scores,
                    benchmark_item.question,
                    benchmark_item.answer,
                    response.llm_answer,
                    response.llm_context_list,
                )
            )
        # Calculate overall scores
        overall_scores: dict[str, float] = {}
        for metric_name in total_scores:
            overall_scores[metric_name] = (
                total_scores[metric_name] / score_counts[metric_name]
            )
        return Run(overall_scores, run_data, None)
