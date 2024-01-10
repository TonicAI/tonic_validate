from pydantic import BaseModel

from tonic_validate.classes.benchmark_item import BenchmarkItem


class LLMResponse(BaseModel):
    llm_answer: str
    llm_context_list: list[str]
    benchmark_item: BenchmarkItem
