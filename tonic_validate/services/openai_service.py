import logging
import os
import time
from typing import Dict
from openai import AzureOpenAI, BadRequestError, OpenAI, RateLimitError
from tiktoken import Encoding

from tonic_validate.classes.exceptions import ContextLengthException, LLMException

logger = logging.getLogger()


class OpenAIService:
    def __init__(
        self,
        encoder: Encoding,
        model: str = "gpt-4-1106-preview",
        starting_wait_time: float = 0.1,
        max_retries: int = 12,
        exp_delay_base: int = 2,
    ) -> None:
        """
        The OpenAIService class is a wrapper around the OpenAI and AzureOpenAI clients.

        Parameters
        ----------
        encoder: Encoding
            The encoding to use for token count.
        model: str
            The model to use for completions.
        starting_wait_time: float
            The starting wait time between retries.
        max_retries: int
            The maximum number of retries to attempt.
        exp_delay_base: int
            Base for exponential back off delay between retries.
        """

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
        self.max_retries = max_retries
        self.exp_delay_base = exp_delay_base
        self.starting_wait_time = starting_wait_time

    def get_response(self, prompt: str) -> str:
        """
        Retrieves a response from the language model

        Parameters
        ----------
        prompt: str
            The prompt to send to the language model.

        Returns
        -------
        str
            The response from the language model.
        """
        if prompt in self.cache:
            return self.cache[prompt]
        num_retries = 0
        wait_time = self.starting_wait_time
        while num_retries < self.max_retries:
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
            except RateLimitError:
                log_message = (
                    "hit openai.error.RateLimitError and entered retry "
                    f"logic, num_retries={num_retries}"
                )
                logger.debug(log_message)
                time.sleep(wait_time)
                wait_time *= self.exp_delay_base
            except Exception as e:
                logger.warning(e)
                time.sleep(wait_time)
                wait_time *= self.exp_delay_base
            num_retries += 1
        raise LLMException(
            f"Failed to get completion response from {self.model}, max retires hit"
        )

    def get_token_count(self, text: str) -> int:
        return len(self.encoder.encode(text))
