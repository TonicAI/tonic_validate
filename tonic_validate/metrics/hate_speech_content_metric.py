import logging

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.utils.llm_calls import contains_hate_speech
from tonic_validate.utils.metrics_util import parse_boolean_response

logger = logging.getLogger()


class HateSpeechContentMetric(BinaryMetric):
    name: str = "hate_speech_content"

    def __init__(self):
        """
        Binary metric that checks whether the response contains hate speech.
        Returns 1 (True) if the response contains hate speech. Returns 0 (False) if it does not contain hate speech.
        """
        super().__init__(self.name, self.metric_callback)

    async def metric_callback(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> bool:
        return parse_boolean_response(
            await contains_hate_speech(llm_response.llm_answer, openai_service)
        )
