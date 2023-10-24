from dataclasses import dataclass
from typing import List

from tvalmetrics.llm_calls import ask_whether_context_is_relevant
from tvalmetrics.scorers.scorers_util import parse_boolean_response


@dataclass
class RetrievalPrecision:
    """Retrieval precision score and information used to calculate the score.

    Fields
    ------
    score: float
        Float between 0 and 1 representing the retrieval precision score.
    question: str
        The question that was asked.
    context_list: List[str]
        Retrieved context used by the RAG system to make answer.
    context_relevant_list: List[bool]
        List of booleans representing whether each context in context_list is relevant
        for answering the question.
    """

    score: float
    question: str
    context_list: List[str]
    context_relevant_list: List[bool]


class RetrievalPrecisionScorer(object):
    """Class for calculating retrieval precision score.

    Parameters
    ----------
    model: str
        Name of the LLM model to use as the LLM evaluator.
    """

    def __init__(self, model: str):
        self.model = model

    def score(self, question: str, context_list: List[str]) -> RetrievalPrecision:
        """Calculate retrieval precision score.

        Parameters
        ----------
        question: str
            The question that was asked.
        context_list: List[str]
            Retrieved context used by the RAG system to make answer.

        Returns
        -------
        RetrievalPrecisionScore
            Retrieval precision score and information used to calculate the score."""
        context_relevant_list = []
        for context in context_list:
            relevance_response = ask_whether_context_is_relevant(
                question, context, self.model
            )
            context_relevant_list.append(parse_boolean_response(relevance_response))

        score = sum(context_relevant_list) / len(context_relevant_list)
        return RetrievalPrecision(score, question, context_list, context_relevant_list)
