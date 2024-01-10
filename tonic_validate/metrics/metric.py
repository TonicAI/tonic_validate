from abc import ABC, abstractmethod

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.services.openai_service import OpenAIService


class Metric(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def score(self, llm_response: LLMResponse, openai_service: OpenAIService) -> float:
        pass
