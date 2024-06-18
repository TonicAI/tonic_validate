import os
import requests
from typing import Any, Dict, List, Optional, Union
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.metrics.metric import Metric, MetricRequirement
from tonic_validate.services.openai_service import OpenAIService
from tonic_validate.services.litellm_service import LiteLLMService


class AnswerContainsPiiMetric(BinaryMetric):
    requirements = {MetricRequirement.LLM_ANSWER}

    def __init__(self, pii_types: List[str], textual_api_key: Optional[str] = None):
        """
        Checks to see if PII is contained in the RAG provided answer.  The types of PII looked for are found in the pii_types list.

        Parameters
        ----------
        pii_types: List[str]
        The list of PII types which are looked for in the RAG answer.  The list of possible options are those available in via tonic-textual. Using this Metric requries a Tonic Textual API key.
        You can create an API key for free at at https://textual.tonic.ai.  You can pass your API key into this constructor OR set TONIC_TEXTUAL_API_KEY in your ENVIRONMENT.

        textual_api_key: Optional[str]
        Your Textual API key.  This value is optional. It is preferred that you set TONIC_TEXTUAL_API_KEY via your ENVIRONMENT.

        """
        try:
            from tonic_textual.api import TonicTextual  # type: ignore
        except ImportError:
            raise ImportError(
                "You must install tonic-textual to use the AnswerContainsPiiMetric. You can install it via pip: pip install tonic-textual"
            )
        self.pii_types = [p.lower() for p in pii_types]
        if textual_api_key is None:
            if os.getenv("TONIC_TEXTUAL_API_KEY") is None:
                raise ValueError(
                    "You must set TONIC_TEXTUAL_API_KEY in your ENV or pass your Textual API key into the constructor."
                )
            self.textual = TonicTextual("https://textual.tonic.ai")
        else:
            self.textual = TonicTextual("https://textual.tonic.ai", textual_api_key)

        super().__init__("answer_contains_pii", self.metric_callback)

    def serialize_config(self):
        return {"pii_types": self.pii_types, "textual_api_key": self.textual.api_key}

    @staticmethod
    def from_config(config: Dict[str, Any]) -> Metric:
        return AnswerContainsPiiMetric(
            pii_types=config["pii_types"],
            textual_api_key=config["textual_api_key"],
        )

    def metric_callback(
        self,
        llm_response: LLMResponse,
        llm_service: Union[LiteLLMService, OpenAIService],
    ) -> bool:
        try:
            response = self.textual.redact(llm_response.llm_answer)
            for d in response.de_identify_results:
                if d.label.lower() in self.pii_types:
                    return True
            return False
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ValueError(
                    "Cannot compute AnswerContainsPiiMetric. Your Textual API Key is INVALID."
                )
        raise ValueError(
            "Cannot compute AnswerContainsPiiMetric. Error occured communicating with Textual.  Please try again later or reach out via GitHub issues."
        )
