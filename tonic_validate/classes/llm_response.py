from pydantic.dataclasses import dataclass
from typing import List, Optional
from typing_extensions import TypedDict

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
        That context that was used to generate the answer
    benchmark_item: BenchmarkItem
        The benchmark item that was used to ask the LLM the question
    """

    llm_answer: str
    llm_context_list: List[str]
    benchmark_item: BenchmarkItem
    run_time: Optional[float] = None


class CallbackLLMResponse(TypedDict):
    """
    The response from a language model for a callback.

    Parameters
    ----------
    llm_answer: str
        The answer from the language model
    llm_context_list: List[str]
        The context that was used to generate the answer
    """

    llm_answer: str
    llm_context_list: List[str]
