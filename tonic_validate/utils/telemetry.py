import json
import os
from typing import List, Optional
import uuid
from tonic_validate.classes.user_info import UserInfo
from tonic_validate.config import (
    TONIC_VALIDATE_TELEMETRY_URL,
    TONIC_VALIDATE_DO_NOT_TRACK,
)
from tonic_validate.utils.http_client import HttpClient
from appdirs import user_data_dir

APP_DIR_NAME = "tonic-validate"

# List of CI/CD environment variables
# 1. Github Actions: GITHUB_ACTIONS
# 2  Gitlab CI/CD: GITLAB_CI
# 3. Azure devops: TF_BUILD
# 4. CircleCI: CI
# 5. Jenkins: JENKINS_URL
# 6. TravisCI: CI
# 7. Bitbucket: CI
env_vars = ["GITHUB_ACTIONS", "GITLAB_CI", "TF_BUILD", "CI", "JENKINS_URL"]


class Telemetry:
    def __init__(self, api_key: Optional[str] = None):
        self.http_client = HttpClient(TONIC_VALIDATE_TELEMETRY_URL, api_key)

    def get_user(self) -> UserInfo:
        app_dir_path = user_data_dir(appname=APP_DIR_NAME)
        user_id_path = os.path.join(app_dir_path, "user.json")
        # check if user_id exists else we create a new uuid and write it to the file
        if os.path.exists(user_id_path):
            with open(user_id_path, "r") as f:
                user_info = json.load(f)
        else:
            user_info: UserInfo = {"user_id": str(uuid.uuid4()), "linked": False}
            json_info = json.dumps(user_info)
            # create the directory if it does not exist
            os.makedirs(app_dir_path, exist_ok=True)
            with open(user_id_path, "w") as f:
                f.write(json_info)
        return user_info

    def __is_ci(self):
        for var in env_vars:
            if os.environ.get(var):
                return True
        return False

    def log_run(self, num_of_questions: int, metrics: List[str]):
        if TONIC_VALIDATE_DO_NOT_TRACK:
            return
        user_id = self.get_user()["user_id"]
        self.http_client.http_post(
            "/runs",
            data={
                "user_id": user_id,
                "num_of_questions": num_of_questions,
                "metrics": metrics,
                "is_ci": self.__is_ci(),
            },
            timeout=5,
        )

    def log_benchmark(self, num_of_questions: int):
        if TONIC_VALIDATE_DO_NOT_TRACK:
            return
        user_id = self.get_user()["user_id"]
        self.http_client.http_post(
            "/benchmarks",
            data={
                "user_id": user_id,
                "num_of_questions": num_of_questions,
                "is_ci": self.__is_ci(),
            },
            timeout=5,
        )

    def link_user(self):
        if TONIC_VALIDATE_DO_NOT_TRACK:
            return
        telemetry_user = self.get_user()
        if telemetry_user["linked"]:
            return
        self.http_client.http_post(
            "/users/link",
            data={"telemetry_user_id": telemetry_user["user_id"]},
            timeout=5,
        )
        # Write the linked user to the file
        telemetry_user["linked"] = True
        app_dir_path = user_data_dir(appname=APP_DIR_NAME)
        user_id_path = os.path.join(app_dir_path, "user.json")
        json_info = json.dumps(telemetry_user)
        with open(user_id_path, "w") as f:
            f.write(json_info)
