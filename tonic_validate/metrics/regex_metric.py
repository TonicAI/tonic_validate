import logging
import re

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.services.openai_service import OpenAIService

logger = logging.getLogger()


class RegexMetric(BinaryMetric):
    def __init__(self, name: str, pattern: str, match_count: int = 1):
        super().__init__(name, self.metric_callback)
        self.text = pattern
        self.match_count = match_count

    def metric_callback(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> bool:
        return self.match_count == len(re.findall(self.text, llm_response.llm_answer))
