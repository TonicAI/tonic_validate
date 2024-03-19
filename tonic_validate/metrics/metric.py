from abc import ABC, abstractmethod

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.services.openai_service import OpenAIService


class Metric(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Metric name for the UI"""
        pass

    @abstractmethod
    async def score(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> float:
        """Calculate the score of the metric"""
        pass
