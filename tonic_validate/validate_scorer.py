from ast import Dict
from typing import List

import openai
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.classes.run_score import Score
from tonic_validate.metrics.answer_similarity_metric import AnswerSimilarityMetric

from tonic_validate.metrics.metric import Metric
from tonic_validate.services.openai_service import OpenAIService


class ValidateScorer:
    def __init__(self, metrics: List[Metric], model_evaluator: str = "gpt-4-1106-preview"):
        self.metrics = metrics
        self.model_evaluator = model_evaluator

    def score_run(self, responses: List[LLMResponse]) -> List[List[Score]]:
        """Calculate metric scores for a list of LLMResponse objects.

        Parameters
        ----------
        responses: List[LLMResponse]
            The list of LLMResponse objects to be scored.

        Returns
        -------
        float
            The score for the list of LLMResponse objects.
        """
        results = []
        for response in responses:
            scores = []
            # We cache per response, so we need to create a new OpenAIService
            openai_service = OpenAIService(self.model_evaluator)
            for metric in self.metrics:
                score = metric.score(response, openai_service)
                scores.append(
                    Score(score=score, metric_name=metric.name, llm_response=response)
                )
            results.append(scores)
        return results
