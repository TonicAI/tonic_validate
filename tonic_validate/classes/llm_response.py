from dataclasses import dataclass
from typing import List, TypedDict

from tonic_validate.classes.benchmark import BenchmarkItem


@dataclass
class LLMResponse:
    llm_answer: str
    llm_context_list: List[str]
    benchmark_item: BenchmarkItem


class CallbackLLMResponse(TypedDict):
    llm_answer: str
    llm_context_list: List[str]
