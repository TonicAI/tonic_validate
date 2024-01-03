import logging
from typing import List, Tuple
from tvalmetrics.classes.llm_response import LLMResponse
from tvalmetrics.metrics.metric import Metric
from tvalmetrics.utils.metrics_util import parse_boolean_response
from tvalmetrics.services.openai_service import OpenAIService
from tvalmetrics.utils.llm_calls import answer_contains_context_call

logger = logging.getLogger()


class AugmentationAccuracyMetric(Metric):
    def score(self, llm_response: LLMResponse, openai_service: OpenAIService) -> float:
        return self.calculate_metric(llm_response, openai_service)[0]

    def calculate_metric(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> Tuple[float, List[bool]]:
        contains_context_list = []
        for context in llm_response.llm_context_list:
            contains_context_response = answer_contains_context_call(
                llm_response.llm_answer, context, openai_service
            )
            contains_context_list.append(
                parse_boolean_response(contains_context_response)
            )

        score = sum(contains_context_list) / len(contains_context_list)
        return (score, contains_context_list)
