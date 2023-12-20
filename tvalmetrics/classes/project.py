from tvalmetrics.classes.chat_objects import Benchmark
from tvalmetrics.utils.http_client import HttpClient
from tvalmetrics.classes.run import Run
from tvalmetrics.services.project_service import ProjectService


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

    def new_run(self) -> Run:
        """Create a new Tonic Validate run.

        Returns
        -------
        Run
            The run that was created.
        """
        run_id = self.project_service.new_run(self.id)
        return Run(run_id, self.benchmark, self.client)
