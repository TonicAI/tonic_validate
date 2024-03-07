import logging
from typing import Optional

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.services.openai_service import OpenAIService

logger = logging.getLogger()


class ResponseLengthMetric(BinaryMetric):
    """Checks that response is within a certain number of characters."""

    def __init__(
        self,
        name: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
    ):
        """
        Create a metric that checks if the length of the LLM response is within a given length.

        Parameters
        ----------
        name: str
            The name of the metric that displays in the UI
        min_length: Optional[int]
            The minimum length of the LLM response
        max_length: Optional[int]
            The maximum length of the LLM response
        """
        super().__init__(name, self.metric_callback)
        self.min_length = min_length
        self.max_length = max_length

    def metric_callback(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> bool:
        if self.min_length and len(llm_response.llm_answer) < self.min_length:
            return False
        if self.max_length and len(llm_response.llm_answer) > self.max_length:
            return False
        return True
