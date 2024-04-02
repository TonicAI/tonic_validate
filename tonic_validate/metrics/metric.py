from abc import ABC, abstractmethod
from typing import Optional

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.services.openai_service import OpenAIService


class Metric(ABC):
    """Abstract class for a metric that can be calculated on an LLM response."""

    """Prompt for the metric. Can be overridden by subclasses if a specific prompt is needed."""
    prompt: Optional[str] = None

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
