import logging
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.services.openai_service import OpenAIService

logger = logging.getLogger()


class LatencyMetric(BinaryMetric):
    name: str = "latency_metric"

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

    # We do async here for consistency even though this method doesn't use async
    async def score(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> float:
        # Check that llm_response.run_time is not None
        if llm_response.run_time is None:
            raise ValueError("No run time provided in LLMResponse")
        if llm_response.run_time > self.target_time:
            return 0.0
        return 1.0
