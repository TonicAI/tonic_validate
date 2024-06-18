import logging
from typing import Any, Awaitable, Callable, Dict, Union

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.metric import Metric
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.services.litellm_service import LiteLLMService
import inspect

logger = logging.getLogger()


class BinaryMetric(Metric):
    @property
    def name(self) -> str:
        return self._name

    def __init__(
        self,
        name: str,
        callback: Callable[
            [LLMResponse, Union[LiteLLMService, OpenAIService]],
            Union[Awaitable[bool], bool],
        ],
    ):
        """
        Create a binary metric with a name and a callback. A binary metric returns either True (1) or False (0).

        Parameters
        ----------
        name: str
            The name of the metric that displays in the UI
        callback: Callable[[LLMResponse, OpenAIService], Union[Awaitable[bool], bool]]
            The callback that takes an LLMResponse and an OpenAIService and returns a boolean.
            The callback can be either an async function or a regular function.
        """
        self._name = name
        self.callback = callback

    def serialize_config(self):
        raise NotImplementedError("Cannot serialize a custom binary metric")

    @staticmethod
    def from_config(config: Dict[str, Any]) -> Metric:
        raise NotImplementedError("Cannot deserialize a custom binary metric")

    async def score(
        self,
        llm_response: LLMResponse,
        llm_service: Union[LiteLLMService, OpenAIService],
    ) -> float:
        if inspect.iscoroutinefunction(self.callback):
            result = await self.callback(llm_response, llm_service)
        else:
            result = self.callback(llm_response, llm_service)
        return 1.0 if result else 0.0
