import logging
from typing import Any, Dict, Union
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.metric import Metric, MetricRequirement
from tonic_validate.utils.metrics_util import (
    parse_boolean_response,
    parse_bullet_list_response,
)
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.services.litellm_service import LiteLLMService
from tonic_validate.utils.llm_calls import (
    main_points_call,
    statement_derived_from_context_call,
    statement_derived_from_context_prompt,
    main_points_prompt,
)

logger = logging.getLogger()


class AnswerConsistencyMetric(Metric):
    name: str = "answer_consistency"
    prompt: str = (
        "-------------------\n"
        f"{main_points_prompt()}\n"
        "-------------------\n"
        f"{statement_derived_from_context_prompt(statement='EXAMPLE STATEMENT', context_list=[])}\n"
        "-------------------\n"
    )
    requirements = {MetricRequirement.LLM_ANSWER, MetricRequirement.LLM_CONTEXT}

    def __init__(self):
        """
        Metric that checks whether the LLM answer contains information that does not come from the context.
        Returns a float between 0 and 1, where 1 is completely consistent and 0 is completely inconsistent.
        """
        pass

    def serialize_config(self):
        return {}

    @staticmethod
    def from_config(config: Dict[str, Any]) -> Metric:
        return AnswerConsistencyMetric()

    async def score(
        self,
        llm_response: LLMResponse,
        llm_service: Union[LiteLLMService, OpenAIService],
    ) -> float:
        main_points_response = await main_points_call(
            llm_response.llm_answer, llm_service
        )
        main_point_list = parse_bullet_list_response(main_points_response)
        main_point_derived_from_context_list = []
        for main_point in main_point_list:
            statement_derived_from_context_response = (
                await statement_derived_from_context_call(
                    main_point, llm_response.llm_context_list, llm_service
                )
            )
            main_point_derived_from_context_list.append(
                parse_boolean_response(statement_derived_from_context_response)
            )
        return sum(main_point_derived_from_context_list) / len(main_point_list)
