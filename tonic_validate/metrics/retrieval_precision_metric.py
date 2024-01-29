import logging
from typing import List, Tuple
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.metric import Metric
from tonic_validate.utils.metrics_util import parse_boolean_response
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.utils.llm_calls import context_relevancy_call

logger = logging.getLogger()


class RetrievalPrecisionMetric(Metric):
    name = "retrieval_precision"

    def score(self, llm_response: LLMResponse, openai_service: OpenAIService) -> float:
        return self.calculate_metric(llm_response, openai_service)[0]

    def calculate_metric(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> Tuple[float, List[bool]]:
        if len(llm_response.llm_context_list) == 0:
            logger.warning(
                "No context provided for retrieval precision metric, "
                "setting score to 0.0"
            )
            return (0.0, [])
        context_relevant_list = []
        for context in llm_response.llm_context_list:
            relevance_response = context_relevancy_call(
                llm_response.benchmark_item.question, context, openai_service
            )
            context_relevant_list.append(parse_boolean_response(relevance_response))

        score = sum(context_relevant_list) / len(context_relevant_list)
        return (score, context_relevant_list)
