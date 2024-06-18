from typing import Any, Dict, List, Optional

from pydantic import ConfigDict, validate_call
import logging

from tonic_validate.config import Config
from tonic_validate.metrics import (
    AnswerSimilarityMetric,
    RetrievalPrecisionMetric,
    AugmentationPrecisionMetric,
    AnswerConsistencyMetric,
)

from tonic_validate.metrics.metric import Metric, MetricRequirement
from tonic_validate.utils.http_client import HttpClient
from tonic_validate.utils.telemetry import Telemetry

logger = logging.getLogger()


class ValidateMonitorer:
    DEFAULT_PARALLELISM_CALLBACK = 1
    DEFAULT_PARALLELISM_SCORING = 50

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(
        self,
        metrics: List[Metric] = [
            RetrievalPrecisionMetric(),
            AugmentationPrecisionMetric(),
            AnswerConsistencyMetric(),
        ],
        api_key: Optional[str] = None,
        quiet: bool = False,
    ):
        """
        Create a Tonic Validate scorer that can work with either OpenAIService or LiteLLMService.

        Parameters
        ----------
        metrics: List[Metric]
            The list of metrics to be used for scoring.
        quiet: bool
            If True, will suppress all logging except errors.
        """
        self.metrics = metrics
        self.quiet = quiet
        logger.setLevel(logging.ERROR if quiet else logging.INFO)

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

    def check_metric_requirements(self):
        if any(
            MetricRequirement.REFERENCE_ANSWER in metric.requirements
            for metric in self.metrics
        ):
            raise ValueError("This metric is not supported for monitoring")

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def log(
        self,
        project_id: str,
        question: str,
        answer: str,
        context_list: Optional[List[str]],
        log_metadata: Optional[Dict[str, Any]] = {},
        tags: Optional[List[str]] = [],
    ):
        self.check_metric_requirements()
        config: Dict[str, Dict[str, Any]] = dict()
        for metric in self.metrics:
            # Get class name for metric
            cls_name = metric.__class__.__name__
            config[cls_name] = metric.serialize_config()
        response = self.client.http_post(
            f"/projects/{project_id}/monitoring/jobs",
            data={
                "reference_question": question,
                "llm_answer": answer,
                "llm_context": context_list,
                "log_metadata": log_metadata,
                "tags": tags,
                "metrics_config": config,
            },
        )
        return response["id"]
