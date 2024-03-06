import logging
import re

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.utils.llm_calls import contains_duplicate_information
from tonic_validate.utils.metrics_util import parse_boolean_response

logger = logging.getLogger()


class DuplicationMetric(BinaryMetric):
    """Checks whether or not there's duplicate information in the response."""

    name: str = "duplication_metric"

    def __init__(self):
        super().__init__(self.name, self.metric_callback)

    def metric_callback(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> bool:
        return parse_boolean_response(
            contains_duplicate_information(llm_response.llm_answer, openai_service)
        )
