from typing import Mapping, Optional

import pytest
import requests

from pybaseball.exceptions import PybaseballHttpError, PybaseballTimeoutError
from pybaseball.network.client import DEFAULT_RETRY_COUNT, RETRY_STATUS_CODES, HttpClient


class FakeTransport:
    def __init__(self, response: requests.Response) -> None:
        self.response = response
        self.requested_url: Optional[str] = None
        self.requested_params: Optional[Mapping[str, object]] = None
        self.requested_headers: Optional[Mapping[str, str]] = None
        self.requested_timeout: Optional[float] = None

    def get(
        self,
        url: str,
        *,
        params: Optional[Mapping[str, object]] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: float,
    ) -> requests.Response:
        self.requested_url = url
        self.requested_params = params
        self.requested_headers = headers
        self.requested_timeout = timeout
        return self.response


class TimeoutTransport:
    def get(
        self,
        url: str,
        *,
        params: Optional[Mapping[str, object]] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: float,
    ) -> requests.Response:
        raise requests.exceptions.Timeout("Timeout")


def make_response(status_code: int, body: bytes = b"") -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response._content = body
    response.url = "https://example.com"
    return response


def test_http_client_get_success_uses_injected_transport() -> None:
    transport = FakeTransport(make_response(200, b"success"))
    client = HttpClient(timeout=5.0, retries=1, transport=transport)

    response = client.get("https://example.com", params={"key": "value"})

    assert response.status_code == 200
    assert response.text == "success"
    assert transport.requested_url == "https://example.com"
    assert transport.requested_params == {"key": "value"}
    assert transport.requested_headers is None
    assert transport.requested_timeout == 5.0


def test_http_client_get_timeout_translates_exception() -> None:
    client = HttpClient(timeout=1.0, retries=2, transport=TimeoutTransport())

    with pytest.raises(PybaseballTimeoutError) as exc_info:
        client.get("https://example.com")

    assert "Timeout" in str(exc_info.value)


def test_http_client_get_http_error_preserves_status_code() -> None:
    client = HttpClient(timeout=5.0, retries=1, transport=FakeTransport(make_response(500)))

    with pytest.raises(PybaseballHttpError) as exc_info:
        client.get("https://example.com")

    assert exc_info.value.status_code == 500
    assert "500 Server Error" in str(exc_info.value)


def test_http_client_default_session_configures_retry_policy() -> None:
    client = HttpClient()
    assert isinstance(client.session, requests.Session)
    adapter = client.session.get_adapter("https://")

    assert adapter.max_retries.total == DEFAULT_RETRY_COUNT
    assert set(adapter.max_retries.status_forcelist) == set(RETRY_STATUS_CODES)
