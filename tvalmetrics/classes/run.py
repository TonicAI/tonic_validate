from tvalmetrics.classes.chat_objects import Benchmark
from tvalmetrics.rag_scores_calculator import Scores
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
        scores: Scores,
    ) -> None:
        # Filter out none values from scores.question_with_answer_id_list
        question_with_answer_id_list = [
            question_with_answer_id
            for question_with_answer_id in scores.question_with_answer_id_list
            if question_with_answer_id is not None
        ]
        
        if len(question_with_answer_id_list) != len(scores.llm_answer_list):
            raise ValueError(
                "Some or none of the provided scores have a question_with_answer associated with them"
            )
        
        for index, question_with_answer_id in enumerate(question_with_answer_id_list):
            llm_answer = scores.llm_answer_list[index]
            if llm_answer is None:
                raise ValueError(
                    "No LLM answer provided"
                )
            self.run_service.log(
                self.id,
                question_with_answer_id,
                llm_answer,
                scores.retrieved_context_list_list[index],
                scores.top_k_context_list_list[index],
                scores.answer_similarity_score_list[index],
                scores.retrieval_precision_list[index],
                scores.augmentation_precision_list[index],
                scores.augmentation_accuracy_list[index],
                scores.answer_consistency_list[index],
                scores.overall_score_list[index],
            )
        return
