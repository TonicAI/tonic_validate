import logging
from typing import Callable

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.metric import Metric
from tonic_validate.services.openai_service import OpenAIService

logger = logging.getLogger()


class BinaryMetric(Metric):
    @property
    def name(self) -> str:
        return self._name

    def __init__(
        self, name: str, callback: Callable[[LLMResponse, OpenAIService], bool]
    ):
        self._name = name
        self.callback = callback

    def score(self, llm_response: LLMResponse, openai_service: OpenAIService) -> float:
        return 1.0 if self.callback(llm_response, openai_service) else 0.0
