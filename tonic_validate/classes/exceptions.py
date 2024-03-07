class LLMException(Exception):
    """
    Base class for all exceptions in the LLM
    """

    pass


class ContextLengthException(LLMException):
    """
    Exception raised when the context length is invalid
    """

    pass
