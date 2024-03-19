import logging
from typing import List, Tuple
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.metric import Metric
from tonic_validate.utils.metrics_util import parse_boolean_response
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.utils.llm_calls import answer_contains_context_call

logger = logging.getLogger()


class AugmentationAccuracyMetric(Metric):
    name: str = "augmentation_accuracy"

    def __init__(self):
        """
        Metric that checks whether the LLM answer includes all of the context.
        Returns a float between 0 and 1. 1 indicates that the answer contains all of the context. 0 indicates that it contains none of the context.
        """
        pass

    async def score(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> float:
        return (await self.calculate_metric(llm_response, openai_service))[0]

    async def calculate_metric(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> Tuple[float, List[bool]]:
        contains_context_list: List[bool] = []
        if len(llm_response.llm_context_list) == 0:
            raise ValueError(
                "No context provided, cannot calculate augmentation accuracy"
            )
        for context in llm_response.llm_context_list:
            contains_context_response = await answer_contains_context_call(
                llm_response.llm_answer, context, openai_service
            )
            contains_context_list.append(
                parse_boolean_response(contains_context_response)
            )

        score = sum(contains_context_list) / len(contains_context_list)
        return (score, contains_context_list)
