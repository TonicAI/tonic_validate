import logging

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.services.openai_service import OpenAIService

logger = logging.getLogger()


class AnswerMatchMetric(BinaryMetric):
    def __init__(self, name: str, answer: str, case_sensitive: bool = False):
        """
        Create a metric that checks if the answer matches a given string.
        Returns 1 (True) if the LLM response matches the given string. Returns 0 (False) if the response does not match.

        Parameters
        ----------
        name: str
            The name of the metric that displays in the UI
        answer: str
            The answer to check if it matches the LLM response
        case_sensitive: bool
            If True, the comparison will be case sensitive
        """
        super().__init__(name, self.metric_callback)
        self.answer = answer
        self.case_sensitive = case_sensitive

    def metric_callback(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> bool:
        if self.case_sensitive:
            return self.answer == llm_response.llm_answer
        return self.answer.lower() == llm_response.llm_answer.lower()
