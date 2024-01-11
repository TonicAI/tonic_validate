import logging
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.metric import Metric
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.utils.llm_calls import similarity_score_call

logger = logging.getLogger()


class AnswerSimilarityMetric(Metric):
    name = "answer_similarity"

    def score(self, llm_response: LLMResponse, openai_service: OpenAIService) -> float:
        similarity_score_response = similarity_score_call(
            llm_response.benchmark_item.question,
            llm_response.benchmark_item.answer,
            llm_response.llm_answer,
            openai_service,
        )
        try:
            similarity_score = float(similarity_score_response)
        except ValueError:
            error_message = (
                f"Failed to parse similarity score {similarity_score} as "
                "float, setting score to 0.0"
            )
            logger.error(error_message)
            similarity_score = 0.0

        return similarity_score
