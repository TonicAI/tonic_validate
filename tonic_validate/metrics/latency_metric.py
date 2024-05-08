import logging
from typing import Any, Dict, Union
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.metrics.metric import Metric, MetricRequirement
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.services.litellm_service import LiteLLMService

logger = logging.getLogger()


class LatencyMetric(BinaryMetric):
    name: str = "latency_metric"
    requirements = {MetricRequirement.LLM_RUN_TIME}

    def __init__(self, target_time: float = 5.0) -> None:
        """
        Measures how long it takes for the LLM to complete a request.
        Returns 0.0 if the LLM takes longer than the target time, and 1.0 otherwise.

        Parameters
        ----------
        target_time: float
            The target time for the model to complete the request in seconds.
        """
        self.target_time = target_time

    def serialize_config(self):
        return {"target_time": self.target_time}

    @staticmethod
    def from_config(config: Dict[str, Any]) -> Metric:
        return LatencyMetric(target_time=config["target_time"])

    # We do async here for consistency even though this method doesn't use async
    async def score(
        self,
        llm_response: LLMResponse,
        llm_service: Union[LiteLLMService, OpenAIService],
    ) -> float:
        # Check that llm_response.run_time is not None
        if llm_response.run_time is None:
            raise ValueError("No run time provided in LLMResponse")
        if llm_response.run_time > self.target_time:
            return 0.0
        return 1.0
