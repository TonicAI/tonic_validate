import logging
from typing import Any, Dict, List, Tuple, Union
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.metric import Metric, MetricRequirement
from tonic_validate.utils.metrics_util import parse_boolean_response
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.services.litellm_service import LiteLLMService
from tonic_validate.utils.llm_calls import (
    answer_contains_context_call,
    answer_contains_context_prompt,
)

logger = logging.getLogger()


class AugmentationAccuracyMetric(Metric):
    name: str = "augmentation_accuracy"
    prompt: str = answer_contains_context_prompt()
    requirements = {MetricRequirement.LLM_ANSWER, MetricRequirement.LLM_CONTEXT}

    def __init__(self):
        """
        Metric that checks whether the LLM answer includes all of the context.
        Returns a float between 0 and 1. 1 indicates that the answer contains all of the context. 0 indicates that it contains none of the context.
        """
        pass

    def serialize_config(self):
        return {}

    @staticmethod
    def from_config(config: Dict[str, Any]) -> Metric:
        return AugmentationAccuracyMetric()

    async def score(
        self,
        llm_response: LLMResponse,
        llm_service: Union[LiteLLMService, OpenAIService],
    ) -> float:
        return (await self.calculate_metric(llm_response, llm_service))[0]

    async def calculate_metric(
        self,
        llm_response: LLMResponse,
        llm_service: Union[LiteLLMService, OpenAIService],
    ) -> Tuple[float, List[bool]]:
        contains_context_list: List[bool] = []
        if len(llm_response.llm_context_list) == 0:
            raise ValueError(
                "No context provided, cannot calculate augmentation accuracy"
            )
        for context in llm_response.llm_context_list:
            contains_context_response = await answer_contains_context_call(
                llm_response.llm_answer, context, llm_service
            )
            contains_context_list.append(
                parse_boolean_response(contains_context_response)
            )

        score = sum(contains_context_list) / len(contains_context_list)
        return (score, contains_context_list)
