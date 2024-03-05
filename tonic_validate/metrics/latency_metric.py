import logging
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.metric import Metric
from tonic_validate.services.openai_service import OpenAIService

logger = logging.getLogger()


class LatencyMetric(Metric):
    name: str = "latency_metric"

    def __init__(self, target_time: float = 5.0) -> None:
        """
        Create a LatencyMetric.

        Parameters
        ----------
        target_time: float
            The target time for the model to complete the request in seconds.
        """
        self.target_time = target_time

    def score(self, llm_response: LLMResponse, openai_service: OpenAIService) -> float:
        # Check that llm_response.run_time is not None
        if llm_response.run_time is None:
            raise ValueError("No run time provided in LLMResponse")
        # Find percentage of target time
        if llm_response.run_time == 0:
            return 1.0
        return min(1.0, self.target_time / llm_response.run_time)
