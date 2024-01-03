from typing import List
from tvalmetrics.classes.llm_response import LLMResponse
from tvalmetrics.metrics.answer_similarity_metric import AnswerSimilarityMetric

from tvalmetrics.metrics.metric import Metric
from tvalmetrics.services.openai_service import OpenAIService


class ValidateScorer:
    def __init__(self, metrics: List[Metric]):
        self.metrics = metrics

    def score(self, results: List[LLMResponse]) -> float:
        openai_service = OpenAIService()
        return 0.0
