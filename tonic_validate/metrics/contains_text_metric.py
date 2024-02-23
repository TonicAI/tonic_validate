import logging
from typing import List, Optional, Union

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.services.openai_service import OpenAIService

logger = logging.getLogger()


class ContainsTextMetric(BinaryMetric):
    def __init__(
        self,
        name: str,
        text: Union[str, List[str]],
        case_sensitive: Optional[bool] = False,
    ):
        super().__init__(name, self.metric_callback)
        self.text = text
        self.case_sensitive = case_sensitive

    def metric_callback(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> bool:
        if isinstance(self.text, list):
            return all(self.contains_text(llm_response, text) for text in self.text)
        return self.contains_text(llm_response, self.text)

    def contains_text(self, llm_response: LLMResponse, text_to_find: str) -> bool:
        if self.case_sensitive:
            return text_to_find in llm_response.llm_answer
        return text_to_find.lower() in llm_response.llm_answer.lower()
