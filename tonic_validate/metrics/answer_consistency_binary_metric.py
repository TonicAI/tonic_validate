import logging
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.utils.metrics_util import parse_boolean_response
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.utils.llm_calls import answer_consistent_with_context_call

logger = logging.getLogger()


class AnswerConsistencyBinaryMetric(BinaryMetric):
    name: str = "answer_consistency_binary"

    def __init__(self):
        """
        Binary metric that checks whether there is information in the LLM answer that does not come from the context.
        Returns either 1 (consistent) or 0 (inconsistent).
        """
        super().__init__(self.name, self.metric_callback)

    async def metric_callback(
        self, llm_response: LLMResponse, openai_service: OpenAIService
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
            llm_response.llm_answer, llm_response.llm_context_list, openai_service
        )
        return parse_boolean_response(hallucination_response)
