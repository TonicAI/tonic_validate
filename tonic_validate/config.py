import os
from dotenv import load_dotenv

load_dotenv()

TONIC_VALIDATE_API_KEY = os.getenv(
    "TONIC_VALIDATE_API_KEY",
)
TONIC_VALIDATE_BASE_URL = os.getenv(
    "TONIC_VALIDATE_BASE_URL", "https://validate.tonic.ai/api/v1"
)
TONIC_VALIDATE_TELEMETRY_URL = os.getenv(
    "TONIC_VALIDATE_TELEMETRY_URL", "https://telemetry.tonic.ai/validate"
)
TONIC_VALIDATE_DO_NOT_TRACK = os.getenv(
    "TONIC_VALIDATE_DO_NOT_TRACK", "false"
).lower() in ("true", "1", "t")
TONIC_VALIDATE_GITHUB_ACTION = os.getenv("TONIC_VALIDATE_GITHUB_ACTION")
