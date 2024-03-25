from typing import Iterator, List, Optional
from pydantic import ConfigDict, validate_call
from pydantic.dataclasses import dataclass
from uuid import UUID

from tonic_validate.utils.telemetry import Telemetry


@dataclass
class BenchmarkItem:
    """
    A benchmark item is a question that is used in a benchmark. It can include an optional answer

    Parameters
    ----------
    question: str
        The question to ask
    answer: Optional[str]
        The preferred or ground truth answer to the question
    benchmark_id: Optional[UUID]
        The identifier of the benchmark that contains the question
    """

    question: str
    answer: Optional[str] = None
    benchmark_id: Optional[UUID] = None


class Benchmark:
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(
        self,
        questions: List[str],
        answers: Optional[List[str]] = None,
        name: Optional[str] = None,
    ):
        """
        A benchmark is a collection of questions and answers that are used to evaluate a model

        Parameters
        ----------
        questions: List[str]
            A list of questions to ask
        answers: Optional[List[str]]
            A list of preferred/ground truth answers to the questions
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
            self.items.append(BenchmarkItem(question=question, answer=answer))

        try:
            self.telemetry.log_benchmark(len(questions))
        except Exception as _:
            pass

    # define iterator
    def __iter__(self) -> Iterator[BenchmarkItem]:
        return iter(self.items)
