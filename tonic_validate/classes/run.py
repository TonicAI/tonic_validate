import logging
from typing import Any, List, Optional, Dict, Union
from dataclasses import dataclass
from uuid import UUID

logger = logging.getLogger()


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

    def to_df(self):
        """
        Convert the run data to a pandas DataFrame

        Returns:
            pd.DataFrame: DataFrame with the run data
        """
        try:
            import pandas as pd
        except ImportError as e:
            logger.error(
                "-------\n"
                "Pandas not found. Please install to convert the run data to a dataframe.\n"
                "-------"
            )
            raise e

        metrics = list(self.overall_scores.keys())
        columns = ["question"] + metrics
        scores = []
        for run in self.run_data:
            run_score = [run.reference_question] + [
                run.scores.get(metric, None) for metric in metrics
            ]
            scores.append(run_score)
        return pd.DataFrame(scores, columns=columns)
