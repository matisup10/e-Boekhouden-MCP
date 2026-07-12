"""Tests for the digital archive MCP tool."""

from __future__ import annotations

import base64

import httpx
import pytest

from eboekhouden_mcp.tools import ToolRegistry, register_all_tools
from eboekhouden_mcp.tools.archive import SendFileToDigitalArchiveTool


@pytest.mark.asyncio
async def test_send_file_to_digital_archive_reports_missing_configuration(tmp_path, monkeypatch):
    """The archive tool should fail clearly when Graph/archive settings are absent."""
    monkeypatch.chdir(tmp_path)
    for key in (
        "EBOEKHOUDEN_ARCHIVE_EMAIL",
        "MS_GRAPH_TENANT_ID",
        "MS_GRAPH_CLIENT_ID",
        "MS_GRAPH_CLIENT_SECRET",
        "MS_GRAPH_SEND_FROM_USER",
        "MS_GRAPH_MAILBOX_USER",
    ):
        monkeypatch.delenv(key, raising=False)

    file_path = tmp_path / "invoice.pdf"
    file_path.write_bytes(b"%PDF test")

    result = await SendFileToDigitalArchiveTool().execute(
        client=None,
        arguments={
            "file_path": str(file_path),
            "invoice_number": "INV-1",
            "vendor_name": "Supplier BV",
        },
    )

    assert result["sent"] is False
    assert result["configured"] is False
    assert result["linked_to_mutation"] is False
    assert "Missing archive/Graph configuration" in result["error"]


@pytest.mark.asyncio
async def test_send_file_to_digital_archive_posts_graph_send_mail_payload(
    tmp_path,
    monkeypatch,
):
    """The archive tool should send the local file to Graph as an email attachment."""
    file_path = tmp_path / "invoice.pdf"
    file_bytes = b"%PDF test invoice"
    file_path.write_bytes(file_bytes)

    monkeypatch.setenv("EBOEKHOUDEN_ARCHIVE_EMAIL", "1594863@e-Boekhouden.nl")
    monkeypatch.setenv("MS_GRAPH_TENANT_ID", "tenant-id")
    monkeypatch.setenv("MS_GRAPH_CLIENT_ID", "client-id")
    monkeypatch.setenv("MS_GRAPH_CLIENT_SECRET", "client-secret")
    monkeypatch.setenv("MS_GRAPH_SEND_FROM_USER", "sender@example.com")

    posts: list[dict] = []

    class FakeClient:
        def __init__(self, timeout):
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, url, **kwargs):
            posts.append({"url": url, **kwargs})
            request = httpx.Request("POST", url)
            if url.endswith("/oauth2/v2.0/token"):
                return httpx.Response(200, json={"access_token": "graph-token"}, request=request)
            return httpx.Response(202, request=request)

    monkeypatch.setattr("eboekhouden_mcp.tools.archive.httpx.Client", FakeClient)

    result = await SendFileToDigitalArchiveTool().execute(
        client=None,
        arguments={
            "file_path": str(file_path),
            "invoice_number": "INV-1",
            "vendor_name": "Supplier BV",
            "mutation_id": 123,
        },
    )

    assert result["sent"] is True
    assert result["configured"] is True
    assert result["linked_to_mutation"] is False
    assert result["mutation_id"] == 123
    assert result["archive_filename"] == "Supplier BV - INV-1.pdf"
    assert "public e-Boekhouden REST API" in result["warning"]

    assert len(posts) == 2
    token_request, send_mail_request = posts
    assert token_request["data"]["client_id"] == "client-id"
    assert token_request["data"]["scope"] == "https://graph.microsoft.com/.default"

    assert send_mail_request["headers"]["Authorization"] == "Bearer graph-token"
    payload = send_mail_request["json"]
    message = payload["message"]
    assert message["toRecipients"][0]["emailAddress"]["address"] == "1594863@e-Boekhouden.nl"
    attachment = message["attachments"][0]
    assert attachment["name"] == "Supplier BV - INV-1.pdf"
    assert attachment["contentType"] == "application/pdf"
    assert attachment["contentBytes"] == base64.b64encode(file_bytes).decode("ascii")


def test_archive_tool_is_registered():
    """The archive tool should be available to MCP clients."""
    registry = ToolRegistry()
    register_all_tools(registry)

    assert "send_file_to_digital_archive" in registry
    assert len(registry) == 49  # 37 base + 12 power tools
