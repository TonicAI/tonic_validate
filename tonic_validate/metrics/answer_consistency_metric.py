import logging
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.metric import Metric
from tonic_validate.utils.metrics_util import (
    parse_boolean_response,
    parse_bullet_list_response,
)
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.utils.llm_calls import (
    main_points_call,
    statement_derived_from_context_call,
)

logger = logging.getLogger()


class AnswerConsistencyMetric(Metric):
    name: str = "answer_consistency"

    def __init__(self):
        """
        Metric that checks whether the LLM answer contains information that does not come from the context.
        Returns a float between 0 and 1, where 1 is completely consistent and 0 is completely inconsistent.
        """
        pass

    async def score(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> float:
        main_points_response = await main_points_call(
            llm_response.llm_answer, openai_service
        )
        main_point_list = parse_bullet_list_response(main_points_response)
        main_point_derived_from_context_list = []
        for main_point in main_point_list:
            statement_derived_from_context_response = (
                await statement_derived_from_context_call(
                    main_point, llm_response.llm_context_list, openai_service
                )
            )
            main_point_derived_from_context_list.append(
                parse_boolean_response(statement_derived_from_context_response)
            )
        return sum(main_point_derived_from_context_list) / len(main_point_list)
