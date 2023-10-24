from typing import List

from tvalmetrics.llm_calls import ask_whether_answer_is_consistent_with_context
from tvalmetrics.scorers.scorers_util import parse_boolean_response


class AnswerConsistencyBinaryScorer(object):
    """Class for calculating answer consistency binary score.

    Parameters
    ----------
    model: str
        Name of the LLM model to use as the LLM evaluator.
    """

    def __init__(self, model: str):
        self.model = model

    def score(self, answer: str, context_list: List[str]) -> int:
        """Calculate answer consistency binary score.

        Parameters
        ----------
        answer: str
            The answer to be scored.
        context_list: List[str]
            Retrieved context used by the RAG system to make answer.

        Returns
        -------
        int
            0 if there is information in answer not derived from context in context_list
            1 otherwise
        """
        hallucination_response = ask_whether_answer_is_consistent_with_context(
            answer, context_list, self.model
        )
        hallucination = parse_boolean_response(hallucination_response)
        return int(hallucination)
