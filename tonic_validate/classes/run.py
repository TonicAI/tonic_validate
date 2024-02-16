from typing import Any, List, Optional, Dict, Union
from dataclasses import dataclass
from uuid import UUID


@dataclass
class RunData:
    scores: Dict[str, Union[float, None]]
    reference_question: str
    reference_answer: Optional[str]
    llm_answer: str
    llm_context: Optional[List[str]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scores": self.scores,
            "reference_question": self.reference_question,
            "reference_answer": self.reference_answer,
            "llm_answer": self.llm_answer,
            "llm_context": self.llm_context,
        }


@dataclass
class Run:
    overall_scores: Dict[str, float]
    run_data: List[RunData]
    id: Optional[UUID]
