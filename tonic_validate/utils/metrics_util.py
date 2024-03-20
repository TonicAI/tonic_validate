import logging
from typing import List

logger = logging.getLogger()


def parse_boolean_response(response: str) -> bool:
    """Parse boolean response from LLM evaluator.

    Attempts to parse response as true or false.

    Parameters
    ----------
    response: str
        Response from LLM evaluator.

    Returns
    -------
    bool
        Whether response should be interpreted as true or false.
    """
    response_lower = response.lower()
    if response_lower == "true":
        return True
    if response_lower == "false":
        return False
    logger.debug(f"Relevance response {response_lower} is not true or false")
    if "true" in response_lower and "false" not in response_lower:
        return True
    if "false" in response_lower and "true" not in response_lower:
        return False
    raise ValueError(
        f"Could not determine true or false from response {response_lower}"
    )


def parse_bullet_list_response(response: str) -> List[str]:
    """Parse bullet list response from LLM evaluator.

    Attempts to parse repsonse as a bullet list, returning a list of strings that
    correspond to the bullet points. The response is assumed to be a bullet list in
    markdown format with the bullet points denoted by asterisks.

    Parameters
    ----------
    response: str
        Response from LLM evaluator.

    Returns
    -------
    List[str]
        List of strings that correspond to the bullet points in the response.
    """

    def get_bullet_list(bullet: str):
        if not response.startswith(bullet):
            log_message = (
                f"Response {response} does not start with bullet, when it should be a "
                "bulleted list. Content before the first bullet will be removed."
            )
            logger.debug(log_message)
        bullet_list = response.split(bullet)[1:]
        bullet_list = [bullet.strip() for bullet in bullet_list]
        if len(bullet_list) == 0:
            raise ValueError(f"Could not parse bullet list from response {response}")
        return bullet_list

    try:
        result = get_bullet_list("*")
    except ValueError:
        result = get_bullet_list("-")
    return result
