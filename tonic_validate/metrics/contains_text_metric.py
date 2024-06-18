import logging
from typing import Any, Dict, List, Optional, Union

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.metrics.metric import Metric, MetricRequirement
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.services.litellm_service import LiteLLMService

logger = logging.getLogger()


class ContainsTextMetric(BinaryMetric):
    """Checks whether or not response contains the given text."""

    requirements = {MetricRequirement.LLM_ANSWER}

    def __init__(
        self,
        name: str,
        text: Union[str, List[str]],
        case_sensitive: Optional[bool] = False,
    ):
        """
        Creates a binary metric that checks whether the LLM response contains a given string.
        Returns 1 (True) if the LLM response contains the string. Returns 0 (False) if it does not contain the string.

        Parameters
        ----------
        name: str
            The name of the metric that displays in the UI
        text: Union[str, List[str]]
            The text to check if it is contained in the LLM response
        case_sensitive: Optional[bool]
            If True, the comparison will be case sensitive
        """
        super().__init__(name, self.metric_callback)
        self.text = text
        self.case_sensitive = case_sensitive

    def serialize_config(self):
        return {
            "name": self.name,
            "text": self.text,
            "case_sensitive": self.case_sensitive,
        }

    @staticmethod
    def from_config(config: Dict[str, Any]) -> Metric:
        return ContainsTextMetric(
            name=config["name"],
            text=config["text"],
            case_sensitive=config["case_sensitive"],
        )

    def metric_callback(
        self,
        llm_response: LLMResponse,
        llm_service: Union[LiteLLMService, OpenAIService],
    ) -> bool:
        if isinstance(self.text, list):
            return all(self.contains_text(llm_response, text) for text in self.text)
        return self.contains_text(llm_response, self.text)

    def contains_text(self, llm_response: LLMResponse, text_to_find: str) -> bool:
        if self.case_sensitive:
            return text_to_find in llm_response.llm_answer
        return text_to_find.lower() in llm_response.llm_answer.lower()
