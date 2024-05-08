import logging
from typing import Any, Dict, List, Tuple, Union
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.metric import Metric, MetricRequirement
from tonic_validate.utils.metrics_util import parse_boolean_response
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.utils.llm_calls import (
    context_relevancy_call,
    context_relevancy_prompt,
)
from tonic_validate.services.litellm_service import LiteLLMService

logger = logging.getLogger()


class RetrievalPrecisionMetric(Metric):
    name: str = "retrieval_precision"
    prompt: str = context_relevancy_prompt()
    requirements = {MetricRequirement.QUESTION, MetricRequirement.LLM_CONTEXT}

    def __init__(self):
        """
        Metric that checks whether the retrieved context is relevant to answer the given question.
        Returns a float between 0 and 1. 1 indicates that all of the context is relevant. 0 indicates that none of the context is relevant.
        """
        pass

    def serialize_config(self):
        return {}

    @staticmethod
    def from_config(config: Dict[str, Any]) -> Metric:
        return RetrievalPrecisionMetric()

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
        if len(llm_response.llm_context_list) == 0:
            raise ValueError(
                "No context provided, cannot calculate retrieval precision"
            )
        context_relevant_list: List[bool] = []
        for context in llm_response.llm_context_list:
            relevance_response = await context_relevancy_call(
                llm_response.benchmark_item.question, context, llm_service
            )
            context_relevant_list.append(parse_boolean_response(relevance_response))

        score = sum(context_relevant_list) / len(context_relevant_list)
        return (score, context_relevant_list)
