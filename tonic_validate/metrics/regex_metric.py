import logging
import re

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.services.openai_service import OpenAIService

logger = logging.getLogger()


class RegexMetric(BinaryMetric):
    """Searches response matching regex."""

    def __init__(self, name: str, pattern: str, match_count: int = 1):
        """
        Create a metric that checks if the answer matches a given regex pattern.

        Parameters
        ----------
        name: str
            The name of the metric that displays in the UI
        pattern: str
            The regex pattern to check if it matches the LLM response
        match_count: int
            The number of matches that should be found in the LLM response
        """
        super().__init__(name, self.metric_callback)
        self.pattern = pattern
        self.match_count = match_count

    def metric_callback(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> bool:
        return self.match_count == len(
            re.findall(self.pattern, llm_response.llm_answer)
        )
