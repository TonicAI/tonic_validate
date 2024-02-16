import os
from typing import List
import uuid
from tonic_validate.config import (
    TONIC_VALIDATE_TELEMETRY_URL,
    TONIC_VALIDATE_DO_NOT_TRACK,
)
from tonic_validate.utils.http_client import HttpClient
from appdirs import user_data_dir

APP_DIR_NAME = "tonic-validate"


class Telemetry:
    def __init__(self):
        self.http_client = HttpClient(TONIC_VALIDATE_TELEMETRY_URL)

    def get_user(self) -> str:
        app_dir_path = user_data_dir(appname=APP_DIR_NAME)
        user_id_path = os.path.join(app_dir_path, "user.txt")
        # check if user_id exists else we create a new uuid and write it to the file
        if os.path.exists(user_id_path):
            with open(user_id_path, "r") as f:
                user_id = f.read()
        else:
            user_id = str(uuid.uuid4())
            # create the directory if it does not exist
            os.makedirs(app_dir_path, exist_ok=True)
            with open(user_id_path, "w") as f:
                f.write(user_id)
        return user_id

    def log_run(self, num_of_questions: int, metrics: List[str]):
        if TONIC_VALIDATE_DO_NOT_TRACK:
            return
        user_id = self.get_user()
        self.http_client.http_post(
            "/runs",
            data={
                "user_id": user_id,
                "num_of_questions": num_of_questions,
                "metrics": metrics,
            },
            timeout=5,
        )

    def log_benchmark(self, num_of_questions: int):
        if TONIC_VALIDATE_DO_NOT_TRACK:
            return
        user_id = self.get_user()
        self.http_client.http_post(
            "/benchmarks",
            data={"user_id": user_id, "num_of_questions": num_of_questions},
            timeout=5,
        )
