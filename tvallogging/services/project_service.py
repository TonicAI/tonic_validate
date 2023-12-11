from typing import Any

from tvallogging.classes.http_client import HttpClient


class ProjectService(object):
    def __init__(self, client: HttpClient):
        self.client = client

    def new_project(self, project_name: str, benchmark_id: str) -> str:
        data = {"name": project_name, "benchmark_id": benchmark_id}
        response = self.client.http_post("/projects/", data=data)
        return response["id"]

    def new_run(self, project_id: str) -> str:
        data = {
            "project_id": project_id,
            "overall_answer_similarity": 0,
            "overall_retrieval_precision": 0,
            "overall_augmentation_precision": 0,
            "overall_augmentation_accuracy": 0,
            "overall_answer_consistency": 0,
            "overall_score": 0,
        }
        response = self.client.http_post("/runs/", data=data)
        return response["id"]

    def get_project(self, project_id: str) -> Any:
        return self.client.http_get(f"/projects/{project_id}")
