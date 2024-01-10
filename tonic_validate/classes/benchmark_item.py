from pydantic import BaseModel


class BenchmarkItem(BaseModel):
    question: str
    reference_answer: str
