from pydantic import BaseModel

from tonic_validate.classes.llm_response import LLMResponse


class Score(BaseModel):
    score: float
    metric_name: str
    llm_response: LLMResponse
