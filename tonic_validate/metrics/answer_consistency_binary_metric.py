import logging
from typing import Any, Dict, Union
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.metrics.metric import Metric, MetricRequirement
from tonic_validate.utils.metrics_util import parse_boolean_response
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.services.litellm_service import LiteLLMService
from tonic_validate.utils.llm_calls import (
    answer_consistent_with_context_call,
    context_consistency_prompt,
)

logger = logging.getLogger()


class AnswerConsistencyBinaryMetric(BinaryMetric):
    name: str = "answer_consistency_binary"
    prompt: str = context_consistency_prompt()
    requirements = {MetricRequirement.LLM_ANSWER, MetricRequirement.LLM_CONTEXT}

    def __init__(self):
        """
        Binary metric that checks whether there is information in the LLM answer that does not come from the context.
        Returns either 1 (consistent) or 0 (inconsistent).
        """
        super().__init__(self.name, self.metric_callback)

    def serialize_config(self):
        return {}

    @staticmethod
    def from_config(config: Dict[str, Any]) -> Metric:
        return AnswerConsistencyBinaryMetric()

    async def metric_callback(
        self,
        llm_response: LLMResponse,
        llm_service: Union[LiteLLMService, OpenAIService],
    ) -> bool:
        """Check if answer is consistent with context.

        Parameters
        ----------
        llm_response: LLMResponse
            The response from the LLM system.
        openai_service: OpenAIService
            The OpenAI service used to make the request.

        Returns
        -------
        bool
            True if answer is consistent with context, False otherwise.
        """
        hallucination_response = await answer_consistent_with_context_call(
            llm_response.llm_answer, llm_response.llm_context_list, llm_service
        )
        return parse_boolean_response(hallucination_response)
