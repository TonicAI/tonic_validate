import logging
from typing import Any, Dict, List, Union
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.augmentation_accuracy_metric import (
    AugmentationAccuracyMetric,
)
from tonic_validate.metrics.metric import Metric
from tonic_validate.metrics.retrieval_precision_metric import RetrievalPrecisionMetric
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.services.litellm_service import LiteLLMService

logger = logging.getLogger()


class AugmentationPrecisionMetric(Metric):
    name: str = "augmentation_precision"
    requirements = AugmentationAccuracyMetric.requirements.union(
        RetrievalPrecisionMetric.requirements
    )

    def __init__(self) -> None:
        """
        Metric that checks whether the LLM answer contains the relevant context.
        Returns a float between 0 and 1. 1 indicates that the answer contains all of the relevant context. 0 indicates that it contains none of the relevant context.
        """
        self.augmentation_accuracy = AugmentationAccuracyMetric()
        self.retrieval_precision = RetrievalPrecisionMetric()

    def serialize_config(self):
        return {}

    @staticmethod
    def from_config(config: Dict[str, Any]) -> Metric:
        return AugmentationPrecisionMetric()

    async def score(
        self,
        llm_response: LLMResponse,
        llm_service: Union[LiteLLMService, OpenAIService],
    ) -> float:
        retrieval_precision_score = await self.retrieval_precision.calculate_metric(
            llm_response, llm_service
        )
        context_relevant_list = retrieval_precision_score[1]
        augmentation_accuracy_score = await self.augmentation_accuracy.calculate_metric(
            llm_response, llm_service
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
