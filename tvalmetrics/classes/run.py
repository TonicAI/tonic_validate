from typing import List, Optional

from tvallogging.chat_objects import QuestionWithAnswer
from tvalmetrics.utils.http_client import HttpClient


class Run(object):
    """Object representing a Tonic Validate run.

    Parameters
    ----------
    id : str
        The ID of the run.
    benchmark : Benchmark
        The benchmark associated with the run.
    scores_calculator : RagScoresCalculator
        The scores calculator used to calculate scores for the run.
    client : HttpClient
        The HTTP client used to make requests to the Tonic Validate API.
    """

    def __init__(
        self,
        id: str,
        client: HttpClient,
    ):
        self.id = id
        self.client = client
    
    def log(
        self,
        question_with_answer: QuestionWithAnswer,
        llm_answer: str,
        retrieved_context_list: Optional[List[str]] = None,
        top_k_context_list: Optional[List[str]] = None,
        answer_similarity: Optional[float] = None,
        retrieval_precision: Optional[float] = None,
        augmentation_precision: Optional[float] = None,
        augmentation_accuracy: Optional[float] = None,
        answer_consistency: Optional[float] = None,
        overall_score: Optional[float] = None,
    ) -> None:
        if question_with_answer.id is None:
            raise ValueError(
                "question id is None, and we need question id to log the answer"
            )

        # for now, we do not do anything with top_k_context_list
        data = {
            "answer_similarity": answer_similarity,
            "retrieval_precision": retrieval_precision,
            "augmentation_precision": augmentation_precision,
            "augmentation_accuracy": augmentation_accuracy,
            "answer_consistency": answer_consistency,
            "overall_score": overall_score,
            "llm_answer": llm_answer,
            "llm_context": retrieved_context_list,
            "question_with_answer_id": question_with_answer.id,
        }
        self.client.http_post(f"/runs/{self.id}/logs", data=data)
        return
