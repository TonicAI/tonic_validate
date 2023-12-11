import os
from typing import Optional

from tvallogging.chat_objects import Benchmark
from tvallogging.classes.http_client import HttpClient
from tvallogging.classes.project import Project
from tvallogging.logging_util import convert_benchmark_response_to_benchmark
from tvallogging.services.benchmark_service import BenchmarkService
from tvallogging.services.project_service import ProjectService


class TonicValidateApi:
    """Wrapper class for invoking the Tonic Validate API.

    Parameters
    ----------
    api_key : str
        The access token for the Tonic Validate API. The access token is obtained from
        the Tonic Validate UI.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://validate.tonic.ai/api/v1",
    ):
        if api_key is None:
            api_key = os.environ.get("TONIC_VALIDATE_API_KEY")
            if api_key is None:
                exception_message = (
                    "No api key provided. Please provide an api key or set "
                    "TONIC_VALIDATE_API_KEY environment variable."
                )
                raise Exception(exception_message)
        self.client = HttpClient(base_url, api_key)
        self.project_service = ProjectService(self.client)
        self.benchmark_service = BenchmarkService(self.client)

    def get_project(self, project_id: str) -> Project:
        """Get a Tonic Validate project by its ID.

        Get a project before starting a run for the project.

        Parameters
        ----------
        project_id : str
            The ID of the project.
        """
        project_response = self.project_service.get_project(project_id)
        benchmark = self.get_benchmark(project_response["benchmark_id"])
        return Project(
            project_response["id"], benchmark, project_response["name"], self.client
        )

    def get_benchmark(self, benchmark_id: str) -> Benchmark:
        """Get a Tonic Validate benchmark by its ID.

        Get a benchmark to create a new project with that benchmark.

        Parameters
        ----------
        benchmark_id : str
            The ID of the benchmark.
        """
        benchmark_response = self.benchmark_service.get_benchmark(benchmark_id)
        benchmark = convert_benchmark_response_to_benchmark(benchmark_response)
        return benchmark

    def new_benchmark(self, benchmark: Benchmark, benchmark_name: str) -> str:
        """Create a new Tonic Validate benchmark.

        Parameters
        ----------
        benchmark : Benchmark
            The benchmark to create.
        benchmark_name : str
            The name of the benchmark.
        """
        benchmark_id = self.benchmark_service.new_benchmark(benchmark_name)

        for question_with_answer in benchmark.question_with_answer_list:
            _ = self.benchmark_service.add_question_with_answer(
                benchmark_id, question_with_answer.question, question_with_answer.answer
            )

        return benchmark_id

    def new_project(self, benchmark_id: str, project_name: str) -> Project:
        """Create a new Tonic Validate project.

        Parameters
        ----------
        benchmark_id : str
            The ID of the benchmark to create the project with.
        project_name : str
            The name of the project.
        """
        project_id = self.project_service.new_project(project_name, benchmark_id)
        benchmark = self.get_benchmark(benchmark_id)
        return Project(project_id, benchmark, project_name, self.client)
