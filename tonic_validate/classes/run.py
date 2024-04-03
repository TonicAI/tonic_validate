import logging
from typing import Any, List, Optional, Dict, Union
from pydantic.dataclasses import dataclass
from uuid import UUID

logger = logging.getLogger()


@dataclass
class RunData:
    """
    Represents the data for a single run.

    Parameters:
    -----------
    scores: Dict[str, Union[float, None]]
        The scores for the run
    reference_question: str
        The reference question
    reference_answer: Optional[str]
        The reference answer
    llm_answer: str
        The answer from the language model
    llm_context: Optional[List[str]]
        The context that was used to generate the answer
    """

    scores: Dict[str, Union[float, None]]
    reference_question: str
    reference_answer: Optional[str]
    llm_answer: str
    llm_context: Optional[List[str]]

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the RunData object to a dictionary.

        Returns:
            Dict[str, Any]: A dictionary representation of the RunData object.
        """
        return {
            "scores": self.scores,
            "reference_question": self.reference_question,
            "reference_answer": self.reference_answer,
            "llm_answer": self.llm_answer,
            "llm_context": self.llm_context,
        }


@dataclass
class Run:
    """
    Represents a run. Includes the run data and the overall scores

    Parameters:
    -----------
    overall_scores: Dict[str, float]
        The overall scores for the run
    run_data: List[RunData]
        The run data
    llm_evaluator: Optional[str]
        The name of the language model evaluator
    id: Optional[UUID]
        The identifier of the run
    """

    overall_scores: Dict[str, float]
    run_data: List[RunData]
    llm_evaluator: Optional[str]
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
