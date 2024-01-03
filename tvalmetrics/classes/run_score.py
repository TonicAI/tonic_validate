from pydantic import BaseModel

from tvalmetrics.classes.llm_response import LLMResponse


class Score(BaseModel):
    score: float
    metric_name: str
    llm_response: LLMResponse
