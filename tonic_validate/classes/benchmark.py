from typing import Iterator, List, Optional
from dataclasses import dataclass
from uuid import UUID

from tonic_validate.utils.telemetry import Telemetry


@dataclass
class BenchmarkItem:
    question: str
    answer: Optional[str] = None
    benchmark_id: Optional[UUID] = None


class Benchmark:
    def __init__(
        self,
        questions: List[str],
        answers: Optional[List[str]] = None,
        name: Optional[str] = None,
    ):
        self.name: Optional[str] = name
        self.items: List[BenchmarkItem] = []
        self.telemetry = Telemetry()

        benchmark_answers = answers
        if benchmark_answers is None:
            benchmark_answers = [None] * len(questions)

        if len(questions) != len(benchmark_answers):
            raise ValueError("Questions and answers must be the same length")
        for question, answer in zip(questions, benchmark_answers):
            self.items.append(BenchmarkItem(question, answer))

        try:
            self.telemetry.log_benchmark(len(questions))
        except Exception as _:
            pass

    # define iterator
    def __iter__(self) -> Iterator[BenchmarkItem]:
        return iter(self.items)
