from typing import Optional

from tvallogging.classes.http_client import HttpClient


class BenchmarkService(object):
    def __init__(self, client: HttpClient):
        self.client = client

    def new_benchmark(self, benchmark_name: str) -> str:
        data = {"name": benchmark_name}
        response = self.client.http_post("/benchmarks/", data=data)
        return response["id"]

    def add_question_with_answer(
        self,
        benchmark_id: str,
        question: str,
        answer: str,
        next_question_with_answer_id: Optional[str] = None,
    ) -> str:
        data = {
            "question": question,
            "answer": answer,
            "next_question_with_answer_id": next_question_with_answer_id,
        }
        response = self.client.http_post(
            f"/benchmarks/{benchmark_id}/question/", data=data
        )
        return response["id"]

    def get_benchmark(self, benchmark_id: str) -> dict:  # type: ignore
        return self.client.http_get(f"/benchmarks/{benchmark_id}")
