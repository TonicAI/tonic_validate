import logging
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.metric import Metric
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.utils.llm_calls import similarity_score_call

logger = logging.getLogger()


class AnswerSimilarityMetric(Metric):
    name: str = "answer_similarity"

    def score(self, llm_response: LLMResponse, openai_service: OpenAIService) -> float:
        # Check that the benchmark item has an answer
        if llm_response.benchmark_item.answer is None:
            raise ValueError("The benchmark item does not have an answer")

        similarity_score_response = similarity_score_call(
            llm_response.benchmark_item.question,
            llm_response.benchmark_item.answer,
            llm_response.llm_answer,
            openai_service,
        )
        try:
            similarity_score = float(similarity_score_response)
        except ValueError:
            raise ValueError(
                f"Failed to parse similarity score {similarity_score_response} as float"
            )

        return similarity_score
