from typing import Any, List, Optional

from tvalmetrics.classes.chat_objects import QuestionWithAnswer
from tvalmetrics.utils.http_client import HttpClient


class RunService(object):
    """Object representing a Tonic Validate run.

    Parameters
    ----------
    id : str
        The ID of the run.
    client : HttpClient
        The HTTP client used to make requests to the Tonic Validate API.
    """

    def __init__(
        self,
        client: HttpClient,
    ):
        self.client = client
    
    def log(
        self,
        run_id: str,
        question_with_answer_id: str,
        llm_answer: str,
        retrieved_context_list: Optional[List[str]] = None,
        top_k_context_list: Optional[List[str]] = None,
        answer_similarity: Optional[float] = None,
        retrieval_precision: Optional[float] = None,
        augmentation_precision: Optional[float] = None,
        augmentation_accuracy: Optional[float] = None,
        answer_consistency: Optional[float] = None,
        overall_score: Optional[float] = None,
    ) -> Any:
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
            "question_with_answer_id": question_with_answer_id
        }
        return self.client.http_post(f"/runs/{run_id}/logs", data=data)
