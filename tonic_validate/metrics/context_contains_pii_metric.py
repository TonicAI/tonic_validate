import os
import requests
from typing import List, Optional
from tonic_validate.classes.llm_response import LLMResponse
from tonic_validate.metrics.binary_metric import BinaryMetric
from tonic_validate.services.openai_service import OpenAIService


class ContextContainsPiiMetric(BinaryMetric):
    def __init__(self, pii_types: List[str], textual_api_key: Optional[str] = None):
        """
        Checks to see if PII is contained in the RAG provided context.  The types of PII looked for are found in the pii_types list.

        Parameters
        ----------
        pii_types: List[str]
        The list of PII types which are looked for in the RAG context.  The list of possible options are those available in via tonic-textual. Using this Metric requries a Tonic Textual API key.
        You can create an API key for free at at https://textual.tonic.ai.  You can pass your API key into this constructor OR set TONIC_TEXTUAL_API_KEY in your ENVIRONMENT.

        textual_api_key: Optional[str]
        Your Textual API key.  This value is optional. It is preferred that you set TONIC_TEXTUAL_API_KEY via your ENVIRONMENT.

        """
        try:
            from tonic_textual.api import TonicTextual
        except ImportError:
            raise ImportError(
                "You must install tonic-textual to use the ContextContainsPiiMetric. You can install it via pip: pip install tonic-textual"
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

        super().__init__("context_contains_pii", self.metric_callback)

    def metric_callback(
        self, llm_response: LLMResponse, openai_service: OpenAIService
    ) -> float:
        try:
            response = self.textual.redact("\n".join(llm_response.llm_context_list))
            for d in response.de_identify_results:
                if d.label.lower() in self.pii_types:
                    return 1.0
            return 0.0
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ValueError(
                    "Cannot compute ContextContainsPiiMetric. Your Textual API Key is INVALID."
                )
        except Exception:
            raise ValueError(
                "Cannot compute ContextContainsPiiMetric. Error occured communicating with Textual.  Please try again later or reach out via GitHub issues."
            )
