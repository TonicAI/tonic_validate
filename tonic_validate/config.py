import os
from dotenv import load_dotenv


class Config:
    def __init__(self) -> None:
        """
        Used to load the configuration from the environment
        """
        load_dotenv()

        self.TONIC_VALIDATE_API_KEY = os.getenv(
            "TONIC_VALIDATE_API_KEY",
        )
        self.TONIC_VALIDATE_BASE_URL = os.getenv(
            "TONIC_VALIDATE_BASE_URL", "https://validate.tonic.ai/api/v1"
        )
        self.TONIC_VALIDATE_TELEMETRY_URL = os.getenv(
            "TONIC_VALIDATE_TELEMETRY_URL", "https://telemetry.tonic.ai/validate"
        )
        self.TONIC_VALIDATE_DO_NOT_TRACK = os.getenv(
            "TONIC_VALIDATE_DO_NOT_TRACK", "false"
        ).lower() in ("true", "1", "t")
        self.TONIC_VALIDATE_GITHUB_ACTION = os.getenv("TONIC_VALIDATE_GITHUB_ACTION")
