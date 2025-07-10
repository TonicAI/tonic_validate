from typing import Any, List, Optional, Dict
from pydantic import ConfigDict, validate_call
from tonic_validate.classes.benchmark import Benchmark
from tonic_validate.classes.run import Run
from warnings import warn

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
        warn("As of 2025-07-30 the Validate API has been turned off and can no longer be used.")

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def upload_run(
        self,
        project_id: str,
        run: Run,
        run_metadata: Optional[Dict[str, Any]] = {},
        tags: Optional[List[str]] = [],
    ) -> str:
        """(This function is deprecated) Upload a run to a Tonic Validate project.

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
        warn("As of 2025-07-30 the Validate API has been turned off and can no longer be used.")

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def get_benchmark(self, benchmark_id: str) -> Benchmark:
        """(This function is deprecated) Get a Tonic Validate benchmark by its ID.

        Get a benchmark to create a new project with that benchmark.

        Parameters
        ----------
        benchmark_id : str
            The ID of the benchmark.
        """
        warn("As of 2025-07-30 the Validate API has been turned off and can no longer be used.")

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def new_benchmark(self, benchmark: Benchmark, benchmark_name: str) -> str:
        """(This function is deprecated) Create a new Tonic Validate benchmark.

        Parameters
        ----------
        benchmark : Benchmark
            The benchmark to create.
        benchmark_name : str
            The name of the benchmark.
        """
        warn("As of 2025-07-30 the Validate API has been turned off and can no longer be used.")
