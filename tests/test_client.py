"""Regression tests for SDK client lifecycle behavior."""

from __future__ import annotations

import json

import httpx

from eboekhouden.client import EBoekhoudenClient, _normalize_session_source


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
