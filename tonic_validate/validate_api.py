from typing import Any, List, Optional, Dict
from pydantic import ConfigDict, validate_call
from tonic_validate.classes.benchmark import Benchmark
from tonic_validate.classes.run import Run
from tonic_validate.config import Config

from tonic_validate.utils.http_client import HttpClient
from tonic_validate.utils.telemetry import Telemetry


class ValidateApi:
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(
        self,
        api_key: Optional[str] = None,
    ):
        """
        Used to interact with the Tonic Validate web application

        Parameters
        ----------
        api_key : str
            The access token for the Tonic Validate application. Obtained from the web application
        """
        self.config = Config()
        if api_key is None:
            api_key = self.config.TONIC_VALIDATE_API_KEY
            if api_key is None:
                exception_message = (
                    "No api key provided. Please provide an api key or set "
                    "TONIC_VALIDATE_API_KEY environment variable."
                )
                raise Exception(exception_message)
        self.client = HttpClient(self.config.TONIC_VALIDATE_BASE_URL, api_key)
        try:
            telemetry = Telemetry(api_key)
            telemetry.link_user()
        except Exception as _:
            pass

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def upload_run(
        self,
        project_id: str,
        run: Run,
        run_metadata: Optional[Dict[str, Any]] = {},
        tags: Optional[List[str]] = [],
    ) -> str:
        """Upload a run to a Tonic Validate project.

        Parameters
        ----------
        project_id : str
            The ID of the project to upload the run to.
        run : Run
            The run to upload.
        run_metadata : Optional[Dict[str, Any]]
            Metadata to attach to the run. If the values are not strings, then they are
            converted to strings before making the request.
        tags : Optional[List[str]]
            A list of tags which can be used to identify this run.  Tags will be rendered in the UI and can also make run searchable.
        """
        if run_metadata and "llm_evaluator" not in run_metadata:
            run_metadata["llm_evaluator"] = run.llm_evaluator
        run_response = self.client.http_post(
            f"/projects/{project_id}/runs/with_data",
            data={
                "run_metadata": run_metadata,
                "tags": tags,
                "data": [run_data.to_dict() for run_data in run.run_data],
            },
        )
        return run_response["id"]

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def get_benchmark(self, benchmark_id: str) -> Benchmark:
        """Get a Tonic Validate benchmark by its ID.

        Get a benchmark to create a new project with that benchmark.

        Parameters
        ----------
        benchmark_id : str
            The ID of the benchmark.
        """
        benchmark_response = self.client.http_get(f"/benchmarks/{benchmark_id}")
        benchmark_items_response = self.client.http_get(
            f"/benchmarks/{benchmark_id}/items"
        )
        questions: List[str] = []
        answers: List[str] = []
        for benchmark_item_response in benchmark_items_response:
            questions += [benchmark_item_response["question"]]
            answers += [benchmark_item_response["answer"]]
        return Benchmark(questions, answers, benchmark_response["name"])

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def new_benchmark(self, benchmark: Benchmark, benchmark_name: str) -> str:
        """Create a new Tonic Validate benchmark.

        Parameters
        ----------
        benchmark : Benchmark
            The benchmark to create.
        benchmark_name : str
            The name of the benchmark.
        """
        benchmark_response = self.client.http_post(
            "/benchmarks", data={"name": benchmark_name}
        )
        for benchmark_item in benchmark.items:
            _ = self.client.http_post(
                f"/benchmarks/{benchmark_response['id']}/items",
                data={
                    "question": benchmark_item.question,
                    "answer": benchmark_item.answer,
                },
            )
        return benchmark_response["id"]
