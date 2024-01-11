from typing import List, Optional
from attr import dataclass
from uuid import UUID


@dataclass
class BenchmarkItem:
    question: str
    answer: Optional[str] = None
    benchmark_id: Optional[UUID] = None


class Benchmark:
    def __init__(
        self, questions: List[str], answers: Optional[List[str]], name: Optional[str]
    ):
        self.name = name
        self.items = []

        if answers is None:
            for question in questions:
                self.items.append(BenchmarkItem(question))
            return

        if len(questions) != len(answers):
            raise ValueError("Questions and answers must be the same length")
        for question, answer in zip(questions, answers):
            self.items.append(BenchmarkItem(question, answer))
