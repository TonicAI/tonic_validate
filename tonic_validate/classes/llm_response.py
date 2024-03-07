from dataclasses import dataclass
from typing import List, TypedDict

from tonic_validate.classes.benchmark import BenchmarkItem


@dataclass
class LLMResponse:
    """
    The response from a language model.

    Parameters
    ----------
    llm_answer: str
        The answer from the language model
    llm_context_list: List[str]
        The context used to generate the answer
    benchmark_item: BenchmarkItem
        The benchmark item used to ask the LLM the question
    """

    llm_answer: str
    llm_context_list: List[str]
    benchmark_item: BenchmarkItem


class CallbackLLMResponse(TypedDict):
    """
    The response from a language model for a callback.

    Parameters
    ----------
    llm_answer: str
        The answer from the language model
    llm_context_list: List[str]
        The context used to generate the answer
    """

    llm_answer: str
    llm_context_list: List[str]
