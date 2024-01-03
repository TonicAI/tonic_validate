import logging
from typing import List
from tvalmetrics.classes.llm_response import LLMResponse
from tvalmetrics.metrics.augmentation_accuracy_metric import AugmentationAccuracyMetric
from tvalmetrics.metrics.metric import Metric
from tvalmetrics.metrics.retrieval_precision_metric import RetrievalPrecisionMetric
from tvalmetrics.utils.metrics_util import parse_boolean_response
from tvalmetrics.services.openai_service import OpenAIService
from tvalmetrics.utils.llm_calls import answer_contains_context_call

logger = logging.getLogger()


class AugmentationPrecisionMetric(Metric):
    name = "augmentation_precision"

    def __init__(self) -> None:
        self.augmentation_accuracy = AugmentationAccuracyMetric()
        self.retrieval_precision = RetrievalPrecisionMetric()

    def score(self, llm_response: LLMResponse, openai_service: OpenAIService) -> float:
        retrieval_precision_score = self.retrieval_precision.calculate_metric(
            llm_response, openai_service
        )
        context_relevant_list = retrieval_precision_score[1]
        augmentation_accuracy_score = self.augmentation_accuracy.calculate_metric(
            llm_response, openai_service
        )
        contains_context_list = augmentation_accuracy_score[1]

        return self.score_from_context_labels(
            context_relevant_list, contains_context_list
        )

    @staticmethod
    def score_from_context_labels(
        context_relevant_list: List[bool], answer_contains_context_list: List[bool]
    ) -> float:
        relevant_context_count = 0
        relevant_context_used_count = 0
        for context_relevant, contains_context in zip(
            context_relevant_list, answer_contains_context_list
        ):
            if context_relevant:
                relevant_context_count += 1
                if contains_context:
                    relevant_context_used_count += 1
        if relevant_context_count == 0:
            augmentation_precision = 0.0
        else:
            augmentation_precision = (
                relevant_context_used_count / relevant_context_count
            )

        return augmentation_precision
