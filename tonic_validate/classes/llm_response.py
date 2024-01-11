from dataclasses import dataclass

from tonic_validate.classes.benchmark_item import BenchmarkItem


@dataclass
class LLMResponse:
    llm_answer: str
    llm_context_list: list[str]
    benchmark_item: BenchmarkItem
