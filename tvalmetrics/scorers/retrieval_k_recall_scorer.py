from dataclasses import dataclass
from typing import List

from tvalmetrics.llm_calls import ask_whether_context_is_relevant
from tvalmetrics.scorers.scorers_util import parse_boolean_response


@dataclass
class RetrievalKRecall:
    """Retrieval k-recall score and information used to calculate the score.

    Fields
    ------
    score: float
        Retrieval k-recall score.
    k: int
        Number of total contexts retrieved.
    retrieved_context_list: List[str]
        Retrieved context used by the RAG system to make answer.
    top_k_context_list: List[str]
        Top k context retrieved by the RAG system. retrieved_context_list is a subset of
        top_k_context_list.
    top_k_context_relevant_list: List[bool]
        List of booleans indicating whether the context is relevant or not to answering
        the question.
    """

    score: float
    k: int
    retrieved_context_list: List[str]
    top_k_context_list: List[str]
    top_k_context_relevant_list: List[bool]


class RetrievalKRecallScorer(object):
    """Class for calculating retrieval k-recall score.

    Parameters
    ----------
    model: str
        Name of the LLM model to use as the LLM evaluator.
    """

    def __init__(self, model: str):
        self.model = model

    def score(
        self,
        question: str,
        retrieved_context_list: List[str],
        top_k_context_list: List[str],
    ) -> RetrievalKRecall:
        """Calculate retrieval k-recall score.

        Parameters
        ----------
        question: str
            The question that was asked.
        retrieved_context_list: List[str]
            Retrieved context used by the RAG system to make answer.
        top_k_context_list: List[str]
            Top k contexts that would be retrieved by the RAG system. There's an
            assumption that the retrieved context list is a subset of the top k context
            list.

        Returns
        -------
        RetrievalKRecallScore
            Retrieval k-recall score and information used to calculate the score.
        """
        k = len(top_k_context_list)
        top_k_context_relevant_list = []
        retrieved_context_relevant_cnt = 0
        for context in top_k_context_list:
            relevance_response = ask_whether_context_is_relevant(
                question, context, self.model
            )
            relevant = parse_boolean_response(relevance_response)
            top_k_context_relevant_list.append(relevant)
            if relevant:
                if context in retrieved_context_list:
                    retrieved_context_relevant_cnt += 1
        if len(top_k_context_relevant_list) == 0:
            score = 0.0
        else:
            score = retrieved_context_relevant_cnt / sum(top_k_context_relevant_list)

        return RetrievalKRecall(
            score,
            k,
            retrieved_context_list,
            top_k_context_list,
            top_k_context_relevant_list,
        )
