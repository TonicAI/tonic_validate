import logging
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.metric import Metric
from tonic_validate.utils.metrics_util import parse_boolean_response
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.utils.llm_calls import answer_consistent_with_context_call

logger = logging.getLogger()


class AnswerConsistencyBinaryMetric(Metric):
    name = "answer_consistency_binary"

    def score(self, llm_response: LLMResponse, openai_service: OpenAIService) -> float:
        """Calculate answer consistency binary score.

        Parameters
        ----------
        answer: str
            The answer to be scored.
        context_list: List[str]
            Retrieved context used by the RAG system to make answer.

        Returns
        -------
        int
            0 if there is information in answer not derived from context in context_list
            1 otherwise
        """
        hallucination_response = answer_consistent_with_context_call(
            llm_response.llm_answer, llm_response.llm_context_list, openai_service
        )
        return float(int(parse_boolean_response(hallucination_response)))
