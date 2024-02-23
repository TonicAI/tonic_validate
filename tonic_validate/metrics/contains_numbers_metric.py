import logging
from typing import List, Union

from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.services.openai_service import OpenAIService

logger = logging.getLogger()


class ContainsNumbersMetric(BinaryMetric):
    def __init__(self, name: str, numbers: List[Union[int, float]]):
        super().__init__(name, self.metric_callback)
        self.numbers = numbers

    def metric_callback(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> bool:
        # extract numbers from the response
        response_numbers = self.extract_numbers(llm_response.llm_answer)

        # check if all numbers are present in the response
        return all(number in response_numbers for number in self.numbers)

    def extract_numbers(self, text: str) -> List[Union[int, float]]:
        # extract numbers from the response
        numbers = []
        for word in text.split():
            try:
                number = float(word)
                numbers.append(number)
            except ValueError:
                pass
        return numbers
