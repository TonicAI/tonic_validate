from typing import Any, Dict, Optional, Union
import requests
from urllib3.exceptions import InsecureRequestWarning  # type: ignore

requests.packages.urllib3.disable_warnings(  # type: ignore
    category=InsecureRequestWarning
)


class HttpClient:
    """Client for handling requests to Tonic Validate instance.

    Parameters
    ----------
    base_url : str
        URL to Tonic Validate instance.
    access_token : str
        The API token associated with your Tonic Validate account.
    """

    def __init__(self, base_url: str, access_token: Optional[str] = None):
        self.base_url = base_url
        self.headers = None
        if access_token is not None:
            self.headers = {"Authorization": f"Bearer {access_token}"}

    def http_get(
        self, url: str, params: Dict[Any, Any] = {}, timeout: Union[int, None] = None
    ) -> Any:
        """Make a get request.

        Parameters
        ----------
        url : str
            URL to make get request. Is appended to self.base_url.
        params: dict
            Passed as the params parameter of the requests.get request.

        """
        res = requests.get(
            self.base_url + url,
            params=params,
            headers=self.headers,
            verify=False,
            timeout=timeout,
        )
        res.raise_for_status()
        return res.json()

    def http_post(
        self,
        url: str,
        params: Dict[Any, Any] = {},
        data: Dict[Any, Any] = {},
        timeout: Union[int, None] = None,
    ) -> Any:
        """Make a post request.

        Parameters
        ----------
        url : str
            URL to make the post request. Is appended to self.base_url.
        params: dict
            Passed as the params parameter of the requests.post request.
        data: dict
            Passed as the data parameter of the requests.post request.
        """
        res = requests.post(
            self.base_url + url,
            params=params,
            json=data,
            headers=self.headers,
            verify=False,
            timeout=timeout,
        )
        res.raise_for_status()
        return res.json()

    def http_put(
        self, url: str, params: Dict[Any, Any] = {}, data: Dict[Any, Any] = {}
    ) -> Any:
        """Make a put request.

        Parameters
        ----------
        url : str
            URL to make the put request. Is appended to self.base_url.
        params: dict
            Passed as the params parameter of the requests.put request.
        data: dict
            Passed as the data parameter of the requests.put request.
        """
        res = requests.put(
            self.base_url + url,
            params=params,
            json=data,
            headers=self.headers,
            verify=False,
        )
        res.raise_for_status()
        return res.json()
