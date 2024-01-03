from abc import ABC, abstractmethod

from tvalmetrics.classes.llm_response import LLMResponse
from tvalmetrics.services.openai_service import OpenAIService


class Metric(ABC):
    @abstractmethod
    def score(self, llm_response: LLMResponse, openai_service: OpenAIService) -> float:
        pass
