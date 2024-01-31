from typing import Iterator, List, Optional, TypedDict

from attr import dataclass


class BenchmarkItem(TypedDict):
    question: str
    answer: Optional[str]


@dataclass
class Benchmark:
    items: List[BenchmarkItem]
    name: Optional[str] = None

    # define iterator
    def __iter__(self) -> Iterator[BenchmarkItem]:
        return iter(self.items)
