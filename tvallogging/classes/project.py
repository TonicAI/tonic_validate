from tvalmetrics import RagScoresCalculator

from tvallogging.chat_objects import Benchmark
from tvallogging.classes.http_client import HttpClient
from tvallogging.classes.run import Run
from tvallogging.services.project_service import ProjectService


class Project(object):
    """Object representing a Tonic Validate project.

    Parameters
    ----------
    id : str
        The ID of the project.
    benchmark : Benchmark
        The benchmark associated with the project.
    name : str
        The name of the project.
    client : HttpClient
        The HTTP client used to make requests to the Tonic Validate API.
    """

    def __init__(self, id: str, benchmark: Benchmark, name: str, client: HttpClient):
        self.id = id
        self.benchmark = benchmark
        self.name = name
        self.client = client
        self.project_service = ProjectService(client)

    def new_run(
        self,
        llm_evaluator: str,
        answer_similarity_score: bool = False,
        retrieval_precision: bool = False,
        augmentation_precision: bool = False,
        augmentation_accuracy: bool = False,
        answer_consistency: bool = False,
        answer_consistency_binary: bool = False,
        retrieval_k_recall: bool = False,
    ) -> Run:
        """Create a new Tonic Validate run.

        If called with just the llm_evaluator parameter, then the run will calculate
        answer similarity score, retrieval precision, augmentation precision,
        augmentation accuracy, and answer consistency.

        Parameters
        ----------
        llm_evaluator : str
            The LLM evaluator to use for the run.
        answer_similarity_score : bool, optional
            Whether to calculate answer similarity score.
        retrieval_precision : bool, optional
            Whether to calculate retrieval precision.
        augmentation_precision : bool, optional
            Whether to calculate augmentation precision.
        augmentation_accuracy : bool, optional
            Whether to calculate augmentation accuracy.
        answer_consistency : bool, optional
            Whether to calculate answer consistency.
        answer_consistency_binary : bool, optional
            Whether to calculate answer consistency binary.
        retrieval_k_recall : bool, optional
            Whether to calculate retrieval k recall.

        Returns
        -------
        Run
            The run that was created.
        """
        # Tonic Validate doesn't currently have answer_consistency_binary or retrieval_k_recall
        if answer_consistency_binary:
            error_message = (
                "Tonic Validate does not currently support answer_consistency_binary"
            )
            raise ValueError(error_message)
        if retrieval_k_recall:
            error_message = (
                "Tonic Validate does not currently support retrieval_k_recall"
            )
            raise ValueError(error_message)
        # if all false, then do default which is answer_similarity_score,
        # retrieval_precisions, augmentation_precision, augmentation_accuracy, and
        # answer_consistency
        if not (
            answer_similarity_score
            or retrieval_precision
            or augmentation_precision
            or augmentation_accuracy
            or answer_consistency
            or answer_consistency_binary
            or retrieval_k_recall
        ):
            answer_similarity_score = True
            retrieval_precision = True
            augmentation_precision = True
            augmentation_accuracy = True
            answer_consistency = True

        scores_calculator = RagScoresCalculator(
            model=llm_evaluator,
            answer_similarity_score=answer_similarity_score,
            retrieval_precision=retrieval_precision,
            augmentation_precision=augmentation_precision,
            augmentation_accuracy=augmentation_accuracy,
            answer_consistency=answer_consistency,
            answer_consistency_binary=answer_consistency_binary,
            retrieval_k_recall=retrieval_k_recall,
        )

        run_id = self.project_service.new_run(self.id)
        return Run(run_id, self.benchmark, scores_calculator, self.client)
