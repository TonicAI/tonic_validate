import logging
from typing import Any, Dict, Union
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.metric import Metric, MetricRequirement
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.services.litellm_service import LiteLLMService
from tonic_validate.utils.llm_calls import (
    similarity_score_call,
    similarity_score_prompt,
)

logger = logging.getLogger()


class AnswerSimilarityMetric(Metric):
    name: str = "answer_similarity"
    prompt: str = similarity_score_prompt()
    requirements = {
        MetricRequirement.QUESTION,
        MetricRequirement.REFERENCE_ANSWER,
        MetricRequirement.LLM_ANSWER,
    }

    def __init__(self) -> None:
        """
        Metric that checks how well the reference answer matches the LLM answer.
        Returns a float between 0 and 5, where 5 is the most similar and 0 is the least similar.
        """
        pass

    def serialize_config(self):
        return {}

    @staticmethod
    def from_config(config: Dict[str, Any]) -> Metric:
        return AnswerSimilarityMetric()

    async def score(
        self,
        llm_response: LLMResponse,
        llm_service: Union[LiteLLMService, OpenAIService],
    ) -> float:
        # Check that the benchmark item has an answer
        if llm_response.benchmark_item.answer is None:
            raise ValueError("The benchmark item does not have an answer")

        similarity_score_response = await similarity_score_call(
            llm_response.benchmark_item.question,
            llm_response.benchmark_item.answer,
            llm_response.llm_answer,
            llm_service,
        )
        try:
            similarity_score = float(similarity_score_response)
        except ValueError:
            raise ValueError(
                f"Failed to parse similarity score {similarity_score_response} as float"
            )
        # Check if similarity_score is within valid range
        if 0 <= similarity_score <= 5:
            return similarity_score
        else:
            raise ValueError(
                f"Similarity score {similarity_score} is not within valid range of 0 to 5"
            )
