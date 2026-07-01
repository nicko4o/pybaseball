from typing import Mapping, Optional, Protocol

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from pybaseball.exceptions import PybaseballHttpError, PybaseballNetworkError, PybaseballTimeoutError

DEFAULT_TIMEOUT_SECONDS = 10.0
DEFAULT_RETRY_COUNT = 3
RETRY_BACKOFF_FACTOR = 1
RETRY_STATUS_CODES = (429, 500, 502, 503, 504)


class HttpTransport(Protocol):
    def get(
        self,
        url: str,
        *,
        params: Optional[Mapping[str, object]] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: float,
    ) -> requests.Response:
        ...


class HttpClient:
    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        retries: int = DEFAULT_RETRY_COUNT,
        transport: Optional[HttpTransport] = None,
    ) -> None:
        self.timeout = timeout
        self.session = transport or self._create_session(retries)

    @staticmethod
    def _create_session(retries: int) -> requests.Session:
        retry_strategy = Retry(
            total=retries,
            backoff_factor=RETRY_BACKOFF_FACTOR,
            status_forcelist=RETRY_STATUS_CODES,
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def get(
        self,
        url: str,
        params: Optional[Mapping[str, object]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> requests.Response:
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout as error:
            raise PybaseballTimeoutError(f"HTTP request timed out: {error}") from error
        except requests.exceptions.HTTPError as error:
            status_code = error.response.status_code if error.response is not None else 500
            raise PybaseballHttpError(f"HTTP error occurred: {error}", status_code=status_code) from error
        except requests.exceptions.RequestException as error:
            raise PybaseballNetworkError(f"HTTP request failed: {error}") from error
