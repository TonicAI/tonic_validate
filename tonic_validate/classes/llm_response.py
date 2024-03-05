from dataclasses import dataclass
from typing import List, Optional, TypedDict

from tonic_validate.classes.benchmark import BenchmarkItem


@dataclass
class LLMResponse:
    llm_answer: str
    llm_context_list: List[str]
    benchmark_item: BenchmarkItem
    run_time: Optional[float] = None


class CallbackLLMResponse(TypedDict):
    llm_answer: str
    llm_context_list: List[str]
