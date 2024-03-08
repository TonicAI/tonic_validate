from typing import TypedDict


class UserInfo(TypedDict):
    """
    Information about a user. Used to provide telemetry

    Parameters
    ----------
    user_id: str
        The identifier of the user
    linked: bool
        Whether the user is linked to an account
    """

    user_id: str
    linked: bool
