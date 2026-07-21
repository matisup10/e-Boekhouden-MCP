"""Regression tests for SDK client lifecycle behavior."""

from __future__ import annotations

import json

import httpx
import pytest

from eboekhouden.client import EBoekhoudenClient, _normalize_session_source
from eboekhouden.exceptions import AuthenticationError, RateLimitError


def test_client_can_be_reused_after_context_manager(monkeypatch) -> None:
    """Re-entering the same client should recreate the closed HTTP transport."""
    requests: list[tuple[str, str]] = []
    session_bodies: list[dict[str, str]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append((request.method, request.url.path))
        if request.method == "POST" and request.url.path == "/v1/session":
            session_bodies.append(json.loads(request.content))
            return httpx.Response(
                200, json={"token": "session-token", "expiresIn": 3600}
            )
        if request.method == "DELETE" and request.url.path == "/v1/session":
            return httpx.Response(204)
        raise AssertionError(f"Unexpected request: {request.method} {request.url.path}")

    def build_mock_http_client(self: EBoekhoudenClient) -> httpx.Client:
        return httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url=self._config.api_url.rstrip("/"),
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )

    monkeypatch.setattr(EBoekhoudenClient, "_build_http_client", build_mock_http_client)

    client = EBoekhoudenClient(
        secret_token="test-token", api_url="https://example.test"
    )
    assert "test-token" not in repr(client._config)

    with client:
        client._ensure_session()

    assert client._http is None

    with client:
        client._ensure_session()

    assert requests == [
        ("POST", "/v1/session"),
        ("DELETE", "/v1/session"),
        ("POST", "/v1/session"),
        ("DELETE", "/v1/session"),
    ]
    assert session_bodies == [
        {"accessToken": "test-token", "source": "PythonSDK"},
        {"accessToken": "test-token", "source": "PythonSDK"},
    ]


def test_session_source_is_sanitized_for_api_pattern() -> None:
    assert _normalize_session_source("Invoice Parser!!!") == "Invoice Pa"
    assert _normalize_session_source("eboekhouden-ai") == "eboekhoude"
    assert _normalize_session_source("") == "PySDK"


def test_authenticated_request_retries_once_with_a_fresh_session(monkeypatch) -> None:
    """An API-expired session should transparently refresh once."""
    session_tokens = iter(["expired-session", "fresh-session"])
    authorization_headers: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/v1/session":
            return httpx.Response(
                200, json={"token": next(session_tokens), "expiresIn": 3600}
            )
        if request.method == "GET" and request.url.path == "/v1/administration":
            token = request.headers["Authorization"]
            authorization_headers.append(token)
            if token == "expired-session":
                return httpx.Response(401, json={"message": "Session expired"})
            return httpx.Response(200, json={"count": 0, "items": []})
        raise AssertionError(f"Unexpected request: {request.method} {request.url.path}")

    def build_mock_http_client(self: EBoekhoudenClient) -> httpx.Client:
        return httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url=self._config.api_url.rstrip("/"),
        )

    monkeypatch.setattr(EBoekhoudenClient, "_build_http_client", build_mock_http_client)

    client = EBoekhoudenClient(
        secret_token="test-token", api_url="https://example.test"
    )
    result = client.administrations.list()

    assert result.count == 0
    assert authorization_headers == ["expired-session", "fresh-session"]


def test_rate_limit_response_exposes_retry_delay(monkeypatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/v1/session":
            return httpx.Response(
                200, json={"token": "session-token", "expiresIn": 3600}
            )
        if request.method == "GET" and request.url.path == "/v1/administration":
            return httpx.Response(
                429,
                headers={"Retry-After": "15"},
                json={"message": "Slow down"},
            )
        raise AssertionError(f"Unexpected request: {request.method} {request.url.path}")

    def build_mock_http_client(self: EBoekhoudenClient) -> httpx.Client:
        return httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url=self._config.api_url.rstrip("/"),
        )

    monkeypatch.setattr(EBoekhoudenClient, "_build_http_client", build_mock_http_client)

    client = EBoekhoudenClient(
        secret_token="test-token", api_url="https://example.test"
    )
    with pytest.raises(RateLimitError) as exc_info:
        client.administrations.list()

    assert exc_info.value.retry_after == 15
    assert exc_info.value.details == {"retry_after": 15}


def test_session_failure_does_not_echo_response_body(monkeypatch) -> None:
    secret_body = "upstream detail that should stay private"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text=secret_body)

    def build_mock_http_client(self: EBoekhoudenClient) -> httpx.Client:
        return httpx.Client(
            transport=httpx.MockTransport(handler),
            base_url=self._config.api_url.rstrip("/"),
        )

    monkeypatch.setattr(EBoekhoudenClient, "_build_http_client", build_mock_http_client)
    client = EBoekhoudenClient(
        secret_token="test-token", api_url="https://example.test"
    )

    with pytest.raises(AuthenticationError) as exc_info:
        client._ensure_session()

    assert "HTTP 500" in str(exc_info.value)
    assert secret_body not in str(exc_info.value)
