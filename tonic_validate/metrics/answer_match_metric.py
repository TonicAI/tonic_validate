import logging

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.services.openai_service import OpenAIService

logger = logging.getLogger()


class AnswerMatchMetric(BinaryMetric):
    def __init__(self, name: str, answer: str, case_sensitive: bool = False):
        super().__init__(name, self.metric_callback)
        self.text = answer
        self.case_sensitive = case_sensitive

    def metric_callback(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> bool:
        if self.case_sensitive:
            return self.text == llm_response.llm_answer
        return self.text.lower() == llm_response.llm_answer.lower()
