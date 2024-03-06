import logging
from typing import Optional

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.services.openai_service import OpenAIService

logger = logging.getLogger()


class ContextLengthMetric(BinaryMetric):
    """Checks that context length is within a certain range."""

    def __init__(
        self,
        name: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
    ):
        super().__init__(name, self.metric_callback)
        self.min_length = min_length
        self.max_length = max_length

    def metric_callback(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> bool:
        # For all items in the context list, check if the length is within the min and max length
        return all(
            self.check_context_length(context)
            for context in llm_response.llm_context_list
        )

    def check_context_length(self, context: str) -> bool:
        if self.min_length and len(context) < self.min_length:
            return False
        if self.max_length and len(context) > self.max_length:
            return False
        return True
