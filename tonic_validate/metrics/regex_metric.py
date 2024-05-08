import logging
import re

from typing import Any, Dict, Union
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.metrics.metric import Metric, MetricRequirement
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.services.litellm_service import LiteLLMService

logger = logging.getLogger()


class RegexMetric(BinaryMetric):
    requirements = {MetricRequirement.LLM_ANSWER}

    def __init__(self, name: str, pattern: str, match_count: int = 1):
        """
        Creates a binary metric that checks whether the answer matches a given regex pattern.
        Returns 1 (True) if the LLM response matches the pattern. Returns 0 (False) if it does not match the pattern.

        Parameters
        ----------
        name: str
            The name of the metric that displays in the UI
        pattern: str
            The regex pattern to check if it matches the LLM response
        match_count: int
            The number of matches that should be found in the LLM response
        """
        super().__init__(name, self.metric_callback)
        self.pattern = pattern
        self.match_count = match_count

    def serialize_config(self):
        return {
            "name": self.name,
            "pattern": self.pattern,
            "match_count": self.match_count,
        }

    @staticmethod
    def from_config(config: Dict[str, Any]) -> Metric:
        return RegexMetric(
            name=config["name"],
            pattern=config["pattern"],
            match_count=config["match_count"],
        )

    def metric_callback(
        self,
        llm_response: LLMResponse,
        llm_service: Union[LiteLLMService, OpenAIService],
    ) -> bool:
        return self.match_count == len(
            re.findall(self.pattern, llm_response.llm_answer)
        )
