from typing import TypedDict


class UserInfo(TypedDict):
    """
    A user info object used for telemetry.

    Parameters
    ----------
    user_id: str
        The user's ID
    linked: bool
        Whether the user is linked to an account
    """

    user_id: str
    linked: bool
