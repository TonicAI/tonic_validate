from typing import Iterator, List, Optional
from dataclasses import dataclass
from uuid import UUID

from tonic_validate.utils.telemetry import Telemetry


@dataclass
class BenchmarkItem:
    """
    A benchmark item is a question and an optional answer used in a benchmark.

    Parameters
    ----------
    question: str
        The question to be asked
    answer: Optional[str]
        The ground truth answer to the question
    benchmark_id: Optional[UUID]
        The ID of the benchmark
    """

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
        """
        A benchmark is a collection of questions and answers used to evaluate a model.

        Parameters
        ----------
        questions: List[str]
            A list of questions to be asked
        answers: Optional[List[str]]
            A list of ground truth answers to the questions
        name: Optional[str]
            The name of the benchmark
        """
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
