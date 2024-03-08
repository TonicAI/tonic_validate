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
        """
        Create a binary metric with a name and a callback. A binary metric returns either True (1) or False (0).

        Parameters
        ----------
        name: str
            The name of the metric that displays in the UI
        callback: Callable[[LLMResponse, OpenAIService], bool]
            The callback that takes an LLMResponse and an OpenAIService and returns a boolean.
        """

        self._name = name
        self.callback = callback

    def score(self, llm_response: LLMResponse, openai_service: OpenAIService) -> float:
        return 1.0 if self.callback(llm_response, openai_service) else 0.0
