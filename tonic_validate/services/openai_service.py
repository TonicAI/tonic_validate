import logging
import os
from typing import Dict
from openai import AzureOpenAI, BadRequestError, OpenAI
from tiktoken import Encoding

from tonic_validate.classes.exceptions import ContextLengthException

logger = logging.getLogger()


class OpenAIService:
    def __init__(self, encoder: Encoding, model: str = "gpt-4-1106-preview") -> None:
        # Check if AZURE_OPENAI_API_KEY is set and if so then use AzureOpenAI
        if "AZURE_OPENAI_API_KEY" in os.environ:
            if "AZURE_OPENAI_ENDPOINT" not in os.environ:
                raise Exception(
                    "AZURE_OPENAI_ENDPOINT must be set in the environment when using AzureOpenAI"
                )
            self.client = AzureOpenAI(api_version="2023-12-01-preview")
        elif "OPENAI_API_KEY" in os.environ:
            self.client = OpenAI()
        else:
            raise Exception(
                "OPENAI_API_KEY or AZURE_OPENAI_API_KEY must be set in the environment"
            )
        self.model = model
        self.encoder = encoder
        self.cache: Dict[str, str] = {}

    def get_response(
        self,
        prompt: str,
        max_retries: int = 5,
    ) -> str:
        if prompt in self.cache:
            return self.cache[prompt]
        while max_retries > 0:
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant. Respond using markdown.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.0,
                )
                response = completion.choices[0].message.content
                if response is None:
                    raise Exception(
                        f"Failed to get message response from {self.model}, message does not exist"
                    )
                self.cache[prompt] = response
                return response
            except BadRequestError as e:
                if e.code == "context_length_exceeded":
                    raise ContextLengthException(e.message)
            except Exception as e:
                logger.warning(e)
                max_retries -= 1
        raise Exception(
            f"Failed to get completion response from {self.model}, max retires hit"
        )

    def get_token_count(self, text: str) -> int:
        return len(self.encoder.encode(text))
