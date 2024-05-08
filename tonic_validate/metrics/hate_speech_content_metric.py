import logging

from typing import Any, Dict, Union
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.metrics.metric import Metric, MetricRequirement
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.services.litellm_service import LiteLLMService
from tonic_validate.utils.llm_calls import (
    contains_hate_speech,
    contains_hate_speech_prompt,
)
from tonic_validate.utils.metrics_util import parse_boolean_response

logger = logging.getLogger()


class HateSpeechContentMetric(BinaryMetric):
    name: str = "hate_speech_content"
    prompt: str = contains_hate_speech_prompt()
    requirements = {MetricRequirement.LLM_ANSWER}

    def __init__(self):
        """
        Binary metric that checks whether the response contains hate speech.
        Returns 1 (True) if the response contains hate speech. Returns 0 (False) if it does not contain hate speech.
        """
        super().__init__(self.name, self.metric_callback)

    def serialize_config(self):
        return {}

    @staticmethod
    def from_config(config: Dict[str, Any]) -> Metric:
        return HateSpeechContentMetric()

    async def metric_callback(
        self,
        llm_response: LLMResponse,
        llm_service: Union[LiteLLMService, OpenAIService],
    ) -> bool:
        return parse_boolean_response(
            await contains_hate_speech(llm_response.llm_answer, llm_service)
        )
