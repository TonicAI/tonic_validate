from typing import Any, List, Optional
from dataclasses import dataclass
from uuid import UUID


@dataclass
class RunData:
    scores: dict[str, float]
    reference_question: str
    reference_answer: Optional[str]
    llm_answer: str
    llm_context: Optional[List[str]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "scores": self.scores,
            "reference_question": self.reference_question,
            "reference_answer": self.reference_answer,
            "llm_answer": self.llm_answer,
            "llm_context": self.llm_context,
        }


@dataclass
class Run:
    overall_scores: dict[str, float]
    run_data: List[RunData]
    id: Optional[UUID]
