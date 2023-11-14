import logging
import time
from typing import Dict, List, Optional, Tuple

from openai import OpenAI, RateLimitError
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from openai.types.completion_usage import CompletionUsage

logger = logging.getLogger()
client = OpenAI()


def make_request_with_retry(
    messages: List[ChatCompletionMessageParam],
    model: str,
    temperature: float,
    wait_time: float = 0.1,
    max_retries: int = 12,
    exp_delay_base: int = 2,
) -> Optional[ChatCompletion]:
    """Makes request to OpenAI API with exponential back off retry logic.

    Parameters
    ----------
    messages: List[ChatCompletionMessageParam]
        List of messages to send to OpenAI API.
    model: str
        Name of the LLM model to use. Must be an Open AI chat completion model.
    temperature: float
        Float between 0 and 1. Temperature to use for Open AI model.
    wait_time: float
        Initial time to wait between retries.
    max_retries: int
        Maximum number of retries before stop retrying.
    exp_delay_base: int
        Base for exponential back off delay between retries.

    Returns
    -------
    Optional[ChatCompletion]
        Response from OpenAI API.
    """
    num_retries = 0
    while num_retries < max_retries:  # if it can't make the request - this is to retry
        try:
            completion = client.chat.completions.create(
                model=model, messages=messages, temperature=temperature
            )
            return completion

        except RateLimitError:
            log_message = (
                "hit openai.error.RateLimitError and entered retry "
                f"logic, num_retries={num_retries}"
            )
            logger.debug(log_message)
            time.sleep(wait_time)
            wait_time *= exp_delay_base
            num_retries += 1
        except Exception as e:
            error_message = (
                "hit non openai.error.RateLimitError exception and "
                f"entered retry logic, num_retries={num_retries}, "
                f"exception {e}"
            )
            logger.error(error_message, exc_info=True)
            time.sleep(wait_time)
            wait_time *= exp_delay_base
            num_retries += 1

    logger.debug(f"reached max retries of {max_retries} for {model} request")
    return None


def get_message_response(
    open_ai_message_list: List[ChatCompletionMessageParam], model: str, temperature: float = 1.0
) -> Tuple[str, CompletionUsage]:
    """Sends message list to Open AI API, parses response, and returns response message.

    Parameters
    ----------
    open_ai_message_list: List[Dict[str, str]]
        List of messages to send to OpenAI API.
    model: str
        Name of the LLM model to use. Must be an Open AI chat completion model.
    temperature: float
        Float between 0 and 1. Temperature to use for Open AI model.

    Returns
    -------
    Tuple[str, CompletionUsage]
        Tuple of response message and usage.
    """
    completion = make_request_with_retry(open_ai_message_list, model, temperature)
    if completion is None:
        raise Exception(f"Failed to get completion response from {model}, max retires hit")

    message_response = completion.choices[0].message.content
    usage = completion.usage
    if message_response is None:
        raise Exception(f"Failed to get message response from {model}, message does not exist")

    return message_response, usage  # type: ignore


def get_single_message(
    message: str,
    model: str,
    temperature: float,
    system_message: str = "You are a helpful assistant. Respond using markdown.",
) -> str:
    """Sets system message and sends message to Open AI API, returns response message.

    Parameters
    ----------
    message: str
        Message to send to OpenAI API.
    model: str
        Name of the LLM model to use. Must be an Open AI chat completion model.
    temperature: float
        Float between 0 and 1. Temperature to use for Open AI model.

    Returns
    -------
    str
        Response from OpenAI API.
    """
    message_list: List[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": message},
    ]

    try:
        response_message, _ = get_message_response(
            message_list, model, temperature=temperature
        )
    except Exception:
        error_message = (
            "An exception occurred while retrieving an answer from "
            f"{model}, using error message as response"
        )
        logging.error(error_message, exc_info=True)
        response_message = error_message

    return response_message
