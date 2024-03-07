class LLMException(Exception):
    """
    The base class for all of the exceptions in the LLM
    """

    pass


class ContextLengthException(LLMException):
    """
    The exception to raise when the context length is invalid
    """

    pass
