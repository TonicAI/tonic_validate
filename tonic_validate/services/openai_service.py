import asyncio
import logging
import os
import random
from openai import AsyncAzureOpenAI, BadRequestError, AsyncOpenAI, RateLimitError
from tiktoken import Encoding

from tonic_validate.classes.exceptions import ContextLengthException, LLMException
from tonic_validate.utils.llm_cache import LLMCache

logger = logging.getLogger()


class OpenAIService:
    def __init__(
        self,
        encoder: Encoding,
        model: str = "gpt-4-1106-preview",
        starting_wait_time: float = 1.0,
        max_retries: int = 10,
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
            self.client = AsyncAzureOpenAI(api_version="2023-12-01-preview")
        elif "OPENAI_API_KEY" in os.environ:
            self.client = AsyncOpenAI()
        else:
            raise Exception(
                "OPENAI_API_KEY or AZURE_OPENAI_API_KEY must be set in the environment"
            )
        self.model = model
        self.encoder = encoder
        self.max_retries = max_retries
        self.exp_delay_base = exp_delay_base
        self.starting_wait_time = starting_wait_time
        self.cache = LLMCache()

    async def get_response(self, prompt: str) -> str:
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

        async def get_openai_response():
            num_retries = 0
            wait_time = self.starting_wait_time
            while num_retries < self.max_retries:
                random_value = random.randrange(0, 20) * 0.01
                wait_time_multiplier = self.exp_delay_base * (1 + random_value)
                try:
                    completion = await self.client.chat.completions.create(
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
                    await asyncio.sleep(wait_time)
                    wait_time *= wait_time_multiplier
                except Exception as e:
                    logger.warning(e)
                    await asyncio.sleep(wait_time)
                    wait_time *= wait_time_multiplier
                num_retries += 1
            raise LLMException(
                f"Failed to get completion response from {self.model}, max retires hit"
            )

        cached_response = self.cache.get(prompt)
        if cached_response is not None:
            return cached_response
        response = await get_openai_response()
        self.cache.put(prompt, response)
        return response

    def get_token_count(self, text: str) -> int:
        return len(self.encoder.encode(text))
