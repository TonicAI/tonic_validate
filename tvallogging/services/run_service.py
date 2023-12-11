from typing import Any, List, Optional

from tvalmetrics.rag_scores_calculator import Scores  # type: ignore

from tvallogging.classes.http_client import HttpClient


class RunService(object):
    def __init__(self, client: HttpClient):
        self.client = client

    def log(
        self,
        run_id: str,
        question_with_answer_id: str,
        llm_answer: str,
        retrieved_context_list: Optional[List[str]],
        top_k_context_list: Optional[List[str]],
        scores: Scores,
    ) -> Any:
        # for now, we do not do anything with top_k_context_list
        data = {
            "answer_similarity": scores.answer_similarity_score,
            "retrieval_precision": scores.retrieval_precision,
            "augmentation_precision": scores.augmentation_precision,
            "augmentation_accuracy": scores.augmentation_accuracy,
            "answer_consistency": scores.answer_consistency,
            "overall_score": scores.overall_score,
            "llm_answer": llm_answer,
            "llm_context": retrieved_context_list,
            "question_with_answer_id": question_with_answer_id,
        }
        return self.client.http_post(f"/runs/{run_id}/logs", data=data)

    def log_metrics(
        self,
        run_id: str,
        question_with_answer_id: str,
        llm_answer: str,
        retrieved_context_list: Optional[List[str]],
        top_k_context_list: Optional[List[str]],
        answer_similarity: Optional[float],
        retrieval_precision: Optional[float],
        augmentation_precision: Optional[float],
        augmentation_accuracy: Optional[float],
        answer_consistency: Optional[float],
        overall_score: Optional[float],
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
            "question_with_answer_id": question_with_answer_id,
        }
        return self.client.http_post(f"/runs/{run_id}/logs", data=data)
