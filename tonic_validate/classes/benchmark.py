from typing import Iterator, List, Optional, TypedDict

from attr import dataclass


class BenchmarkItem(TypedDict):
    question: str
    answer: Optional[str]


@dataclass
class Benchmark:
    name: Optional[str]
    items: List[BenchmarkItem]

    # define iterator
    def __iter__(self) -> Iterator[BenchmarkItem]:
        return iter(self.items)
