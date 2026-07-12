"""Tests for the MCP server wrapper."""

import pytest

from eboekhouden_mcp.config import MCPConfig
from eboekhouden_mcp.server import EBoekhoudenMCPServer


@pytest.mark.asyncio
async def test_get_client_creates_sdk_client_from_mcp_config():
    """The MCP server should pass config values using the SDK keyword API."""
    server = EBoekhoudenMCPServer(
        MCPConfig(
            secret_token="test-token",
            api_url="https://example.test/",
            source="MCP-Server",
        )
    )

    async with server.get_client() as client:
        assert client._config.secret_token == "test-token"
        assert client._config.api_url == "https://example.test/"
        assert client._config.source == "MCPServer"

    server.close()
