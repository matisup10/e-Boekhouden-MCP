"""MCP server for the e-Boekhouden Dutch accounting API."""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from eboekhouden import EBoekhoudenClient, EBoekhoudenConfig
from eboekhouden.exceptions import EBoekhoudenError

from eboekhouden_mcp.config import MCPConfig
from eboekhouden_mcp.tools import ToolRegistry, register_all_tools

logger = logging.getLogger(__name__)


class EBoekhoudenMCPServer:
    """MCP server wrapping the e-Boekhouden SDK."""

    def __init__(self, config: MCPConfig) -> None:
        self.config = config
        self.registry = ToolRegistry()
        self._client: EBoekhoudenClient | None = None

        # Register all tools
        register_all_tools(self.registry)

        # Create SDK config
        self._sdk_config = EBoekhoudenConfig(
            secret_token=config.secret_token,
            api_url=config.api_url,
            source=config.source,
        )

    @asynccontextmanager
    async def get_client(self) -> AsyncIterator[EBoekhoudenClient]:
        """Get an authenticated e-Boekhouden client."""
        if self._client is None:
            self._client = EBoekhoudenClient(
                secret_token=self._sdk_config.secret_token,
                api_url=self._sdk_config.api_url,
                source=self._sdk_config.source,
            )

        try:
            yield self._client
        except Exception:
            # On error, close and reset client
            if self._client is not None:
                self._client.close()
                self._client = None
            raise

    def close(self) -> None:
        """Close the client connection."""
        if self._client is not None:
            self._client.close()
            self._client = None


def create_server(config: MCPConfig | None = None) -> Server:
    """Create and configure the MCP server.

    Args:
        config: Optional configuration. If not provided, loads from environment.

    Returns:
        Configured MCP server instance
    """
    if config is None:
        config = MCPConfig()

    mcp_server = EBoekhoudenMCPServer(config)
    server = Server(config.server_name)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools."""
        tools = []
        for tool in mcp_server.registry.list_tools():
            tools.append(
                Tool(
                    name=tool.name,
                    description=tool.description,
                    inputSchema=tool.get_schema(),
                )
            )
        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Execute a tool by name."""
        tool = mcp_server.registry.get(name)
        if tool is None:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": f"Unknown tool: {name}"}),
                )
            ]

        try:
            async with mcp_server.get_client() as client:
                result = await tool.execute(client, arguments or {})
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(result, default=str, ensure_ascii=False),
                    )
                ]
        except EBoekhoudenError as e:
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "error": str(e),
                            "code": getattr(e, "code", None),
                            "details": getattr(e, "details", None),
                        },
                        default=str,
                    ),
                )
            ]
        except Exception as e:
            logger.exception(f"Error executing tool {name}")
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": str(e)}),
                )
            ]

    return server


async def run_server(config: MCPConfig | None = None) -> None:
    """Run the MCP server with stdio transport."""
    server = create_server(config)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    """Entry point for the MCP server."""
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
