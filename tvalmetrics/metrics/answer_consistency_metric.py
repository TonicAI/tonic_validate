import logging
from tvalmetrics.classes.llm_response import LLMResponse
from tvalmetrics.metrics.metric import Metric
from tvalmetrics.utils.metrics_util import (
    parse_boolean_response,
    parse_bullet_list_response,
)
from tvalmetrics.services.openai_service import OpenAIService
from tvalmetrics.utils.llm_calls import (
    main_points_call,
    statement_derived_from_context_call,
)

logger = logging.getLogger()


class AnswerConsistencyBinaryMetric(Metric):
    def score(self, llm_response: LLMResponse, openai_service: OpenAIService) -> float:
        main_points_response = main_points_call(llm_response.llm_answer, openai_service)
        main_point_list = parse_bullet_list_response(main_points_response)
        main_point_derived_from_context_list = []
        for main_point in main_point_list:
            statement_derived_from_context_response = (
                statement_derived_from_context_call(
                    main_point, llm_response.llm_context_list, openai_service
                )
            )
            main_point_derived_from_context_list.append(
                parse_boolean_response(statement_derived_from_context_response)
            )
        return sum(main_point_derived_from_context_list) / len(main_point_list)
