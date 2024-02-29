import logging
import re

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.utils.llm_calls import is_statement_hate_speech
from tonic_validate.utils.metrics_util import parse_boolean_response

logger = logging.getLogger()





class HateSpeechContentMetric(BinaryMetric):
    name: str = "offensive_content"

    def __init__(self):
        super().__init__(self.name, self.metric_callback)

    def metric_callback(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> bool:
        return parse_boolean_response(
            is_statement_hate_speech(llm_response.llm_answer, openai_service)
        )
