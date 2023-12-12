from typing import List, Optional

from tvalmetrics.classes.chat_objects import Benchmark, QuestionWithAnswer
from tvalmetrics.utils.http_client import HttpClient
from tvalmetrics.services.run_service import RunService


class Run(object):
    """Object representing a Tonic Validate run.

    Parameters
    ----------
    id : str
        The ID of the run.
    benchmark : Benchmark
        The benchmark associated with the run.
    client : HttpClient
        The HTTP client used to make requests to the Tonic Validate API.
    """

    def __init__(
        self,
        id: str,
        benchmark: Benchmark,
        client: HttpClient,
    ):
        self.id = id
        self.benchmark = benchmark
        self.client = client
        self.run_service = RunService(client)
    
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

        self.run_service.log(
            self.id,
            question_with_answer.id,
            llm_answer,
            retrieved_context_list,
            top_k_context_list,
            answer_similarity,
            retrieval_precision,
            augmentation_precision,
            augmentation_accuracy,
            answer_consistency,
            overall_score,
        )
        return
