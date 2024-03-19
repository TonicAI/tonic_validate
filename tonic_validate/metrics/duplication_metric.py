import logging
import re

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.utils.llm_calls import contains_duplicate_information
from tonic_validate.utils.metrics_util import parse_boolean_response

logger = logging.getLogger()


class DuplicationMetric(BinaryMetric):
    name: str = "duplication_metric"

    def __init__(self):
        """
        Binary metric that checks whether the response contains duplicate information.
        Returns 1 (True) if the response contains duplicate information. Returns 0 (False) if it does not contain duplicate information.
        """
        super().__init__(self.name, self.metric_callback)

    async def metric_callback(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> bool:
        return parse_boolean_response(
            await contains_duplicate_information(
                llm_response.llm_answer, openai_service
            )
        )
