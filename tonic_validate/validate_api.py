from typing import List, Optional
from tonic_validate.classes.benchmark import Benchmark
from tonic_validate.classes.run import MetadataDict, Run
from tonic_validate.config import Config

from tonic_validate.utils.http_client import HttpClient
from tonic_validate.utils.telemetry import Telemetry


class ValidateApi:
    """Wrapper class for invoking the Tonic Validate UI.

    Parameters
    ----------
    api_key : str
        The access token for the Tonic Validate UI. The access token is obtained from
        the Tonic Validate UI.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
    ):
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

    def upload_run(
        self, project_id: str, run: Run, run_metadata: MetadataDict = {}
    ) -> str:
        """Upload a run to a Tonic Validate project.

        Parameters
        ----------
        project_id : str
            The ID of the project to upload the run to.
        run : Run
            The run to upload.
        run_metadata : Dict[str, Union[str, Dict[str, str]]]
            Metadata to attach to the run. If the values are not strings, then they are
            converted to strings before making the request.
        """

        # Convert all items in run_metadata to strings (including nested items)
        processed_run_metadata = {}
        for key, value in run_metadata.items():
            if isinstance(value, dict):
                processed_run_metadata[key] = {}
                for nested_key, nested_value in value.items():
                    processed_run_metadata[key][nested_key] = str(nested_value)
            else:
                processed_run_metadata[key] = str(value)
        run_response = self.client.http_post(f"/projects/{project_id}/runs")
        run_response = self.client.http_put(
            f"/projects/{project_id}/runs/{run_response['id']}",
            data={"run_metadata": processed_run_metadata},
        )
        for run_data in run.run_data:
            _ = self.client.http_post(
                f"/projects/{project_id}/runs/{run_response['id']}/logs",
                data=run_data.to_dict(),
            )
        return run_response["id"]

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
