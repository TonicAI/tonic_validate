from typing import List, Optional

from tvalmetrics import RagScoresCalculator

from tvallogging.chat_objects import Benchmark, QuestionWithAnswer
from tvallogging.classes.http_client import HttpClient
from tvallogging.services.run_service import RunService


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
        benchmark: Benchmark,
        scores_calculator: RagScoresCalculator,
        client: HttpClient,
    ):
        self.id = id
        self.benchmark = benchmark
        self.client = client
        self.run_service = RunService(client)
        self.score_calculator = scores_calculator

    def log(
        self,
        question_with_answer: QuestionWithAnswer,
        llm_answer: str,
        retrieved_context_list: Optional[List[str]] = None,
        top_k_context_list: Optional[List[str]] = None,
    ) -> None:
        """Log the answer and retrieved context for a question in the run.

        When you log an answer, Tonic Validate will calculate the scores specified when
        the run was created. The scores are calculated using the tvalmetrics package.

        Parameters
        ----------
        question_with_answer : QuestionWithAnswer
            The question and reference from the benchmark.
        llm_answer : str
            The answer from the RAG system.
        retrieved_context_list : List[str], optional
            The retrieved context from the RAG system used to generate the answer.
        top_k_context_list : List[str], optional
            The top k retrieved contexts from the RAG system. This is only needed if
            calculated the retrieval k-recall score.
        """
        if question_with_answer.id is None:
            raise ValueError(
                "question id is None, and we need question id to log the answer"
            )

        scores = self.score_calculator.score(
            question=question_with_answer.question,
            reference_answer=question_with_answer.answer,
            llm_answer=llm_answer,
            retrieved_context_list=retrieved_context_list,
            top_k_context_list=top_k_context_list,
        )

        self.log_metrics(
            question_with_answer,
            llm_answer,
            retrieved_context_list,
            top_k_context_list,
            scores.answer_similarity_score_list[0],
            scores.retrieval_precision_list[0],
            scores.augmentation_precision_list[0],
            scores.augmentation_accuracy_list[0],
            scores.answer_consistency_list[0],
            scores.overall_score_list[0],
        )
        return

    def log_metrics(
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

        _ = self.run_service.log_metrics(
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
