import asyncio
import logging
import os
import random
from litellm import acompletion, ModelResponse, Choices
from openai import APIConnectionError, BadRequestError, RateLimitError
from tiktoken import Encoding

from tonic_validate.classes.exceptions import LLMException, ContextLengthException
from tonic_validate.utils.llm_cache import LLMCache

logger = logging.getLogger()


class LiteLLMService:
    def __init__(
        self,
        encoder: Encoding,
        model: str = "gemini/gemini-1.5-pro-latest",
        starting_wait_time: float = 1.5,
        max_retries: int = 12,
        exp_delay_base: int = 2,
    ) -> None:
        """
        The LiteLLMService class is a wrapper around LiteLLM client for async operations using different LLMs.

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
        try:
            self.check_environment(model)
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            raise e
        self.model = model
        self.encoder = encoder
        self.max_retries = max_retries
        self.exp_delay_base = exp_delay_base
        self.starting_wait_time = starting_wait_time
        self.cache = LLMCache()

    def check_environment(self, model: str) -> None:
        if "gemini" in model:
            if "GEMINI_API_KEY" not in os.environ:
                raise Exception(
                    "GEMINI_API_KEY must be set in the environment when using Gemini"
                )
        elif "claude" in model:
            if "ANTHROPIC_API_KEY" not in os.environ:
                raise Exception(
                    "ANTHROPIC_API_KEY must be set in the environment when using Claude"
                )
        else:
            raise Exception("Model not supported. Please check the model name.")

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

        async def get_litellm_response():
            num_retries = 0
            wait_time = self.starting_wait_time
            while num_retries < self.max_retries:
                random_value = random.randrange(0, 20) * 0.01
                wait_time_multiplier = self.exp_delay_base * (1 + random_value)
                try:
                    messages = [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant. Respond using markdown.",
                        },
                        {"role": "user", "content": prompt},
                    ]
                    response = await acompletion(
                        model=self.model,
                        messages=messages,
                        temperature=0.0,
                    )
                    # Check that type is ModelResponse
                    if not isinstance(response, ModelResponse):
                        raise Exception(
                            f"Failed to get response from {self.model}, response is not a ModelResponse"
                        )
                    choice = response.choices[0]
                    if not isinstance(choice, Choices):
                        raise Exception(
                            f"Failed to get response from {self.model}, choice is not a Choices object"
                        )
                    response_content = choice.message.content
                    if response_content is None:
                        raise Exception(
                            f"Failed to get message response from {self.model}, message does not exist"
                        )
                    return response_content
                except BadRequestError as e:
                    if e.code == "context_length_exceeded":
                        raise ContextLengthException(e.message)
                except APIConnectionError as e:
                    raise LLMException(e.message)
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
        response = await get_litellm_response()
        self.cache.put(prompt, response)
        return response

    def get_token_count(self, text: str) -> int:
        """
        Gets the token count for the given text using the specified encoder.

        Parameters
        ----------
        text: str
            The text to get the token count for.

        Returns
        -------
        int
            The number of tokens in the text.
        """
        return len(self.encoder.encode(text))
