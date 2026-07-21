"""Tests for the MCP server wrapper."""

import pytest
from mcp.types import CallToolRequest, CallToolRequestParams, ListToolsRequest
from pydantic import ValidationError

from eboekhouden_mcp.config import MCPConfig
from eboekhouden_mcp.server import EBoekhoudenMCPServer, create_server


@pytest.mark.asyncio
async def test_get_client_creates_sdk_client_from_mcp_config():
    """The MCP server should pass config values using the SDK keyword API."""
    server = EBoekhoudenMCPServer(
        MCPConfig(
            secret_token="test-token",
            api_url="https://example.test/",
            source="MCP-Server",
            allow_custom_api_url=True,
        )
    )

    async with server.get_client() as client:
        assert client._config.secret_token.get_secret_value() == "test-token"
        assert "test-token" not in repr(client._config)
        assert client._config.api_url == "https://example.test/"
        assert client._config.source == "MCPServer"

    server.close()


def test_secret_is_redacted_from_config_representation():
    config = MCPConfig(secret_token="test-token", _env_file=None)

    assert "test-token" not in repr(config)
    assert "**********" in repr(config)


def test_custom_api_url_requires_explicit_override():
    with pytest.raises(ValidationError, match="ALLOW_CUSTOM_API_URL"):
        MCPConfig(
            secret_token="test-token",
            api_url="https://example.test/",
            _env_file=None,
        )


def test_empty_token_is_rejected():
    with pytest.raises(ValidationError, match="must not be empty"):
        MCPConfig(secret_token="   ", _env_file=None)


def test_server_defaults_to_read_only_tool_policy():
    server = EBoekhoudenMCPServer(MCPConfig(secret_token="test-token", _env_file=None))

    assert server.tool_is_enabled("list_relations") is True
    assert server.tool_is_enabled("create_relation") is False
    assert server.tool_is_enabled("send_file_to_digital_archive") is False


def test_archive_requires_both_write_flags_and_allowed_root(tmp_path):
    server = EBoekhoudenMCPServer(
        MCPConfig(
            secret_token="test-token",
            enable_write_tools=True,
            enable_archive_tool=True,
            archive_root=tmp_path,
            _env_file=None,
        )
    )

    assert server.tool_is_enabled("create_relation") is True
    assert server.tool_is_enabled("send_file_to_digital_archive") is True


@pytest.mark.asyncio
async def test_default_mcp_surface_exposes_only_annotated_read_tools():
    server = create_server(MCPConfig(secret_token="test-token", _env_file=None))

    result = await server.request_handlers[ListToolsRequest](ListToolsRequest())
    tools = result.root.tools

    assert len(tools) == 34
    assert "create_relation" not in {tool.name for tool in tools}
    assert all(tool.annotations.readOnlyHint is True for tool in tools)
    assert all(tool.annotations.destructiveHint is False for tool in tools)


@pytest.mark.asyncio
async def test_write_surface_has_side_effect_annotations():
    server = create_server(
        MCPConfig(
            secret_token="test-token",
            enable_write_tools=True,
            _env_file=None,
        )
    )

    result = await server.request_handlers[ListToolsRequest](ListToolsRequest())
    tools = {tool.name: tool for tool in result.root.tools}

    assert len(tools) == 48
    assert tools["create_relation"].annotations.readOnlyHint is False
    assert tools["create_relation"].annotations.destructiveHint is False
    assert "confirm" in tools["create_relation"].inputSchema["required"]
    assert tools["create_relation"].inputSchema["properties"]["confirm"] == {
        "type": "boolean",
        "description": (
            "Set to true only after the user explicitly confirms this exact write "
            "action and its identifiers and values."
        ),
    }
    assert tools["delete_relation"].annotations.destructiveHint is True
    assert "send_file_to_digital_archive" not in tools


@pytest.mark.asyncio
async def test_write_call_requires_explicit_confirmation_before_api_access():
    server = create_server(
        MCPConfig(
            secret_token="test-token",
            enable_write_tools=True,
            _env_file=None,
        )
    )

    result = await server.request_handlers[CallToolRequest](
        CallToolRequest(
            params=CallToolRequestParams(
                name="create_relation",
                arguments={"name": "Example", "confirm": False},
            )
        )
    )

    assert result.root.isError is True
    assert "Explicit write confirmation required" in result.root.content[0].text
