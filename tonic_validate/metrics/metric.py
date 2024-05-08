from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Set, Union
from enum import Enum

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.services.litellm_service import LiteLLMService


class MetricRequirement(str, Enum):
    QUESTION = "QUESTION"
    REFERENCE_ANSWER = "REFERENCE_ANSWER"
    LLM_ANSWER = "LLM_ANSWER"
    LLM_CONTEXT = "LLM_CONTEXT"
    LLM_RUN_TIME = "LLM_RUN_TIME"


class Metric(ABC):
    """Abstract class for a metric that can be calculated on an LLM response."""

    # Prompt for the metric
    prompt: Optional[str] = None

    # List of requirements for the metric
    requirements: Set[MetricRequirement]

    @property
    @abstractmethod
    def name(self) -> str:
        """Metric name for the UI"""
        pass

    @staticmethod
    @abstractmethod
    def from_config(config: Dict[str, Any]) -> "Metric":
        """Creates a metric object from a JSON object"""
        pass

    @abstractmethod
    def serialize_config(self) -> Dict[str, Any]:
        """Serializes the metric configuration to a JSON object"""
        pass

    @abstractmethod
    async def score(
        self,
        llm_response: LLMResponse,
        llm_service: Union[LiteLLMService, OpenAIService],
    ) -> float:
        """Calculate the score of the metric"""
        pass
