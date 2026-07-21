"""MCP server for the e-Boekhouden Dutch accounting API."""

from __future__ import annotations

import json
import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, TextContent, Tool, ToolAnnotations
from pydantic import ValidationError

from eboekhouden import EBoekhoudenClient, EBoekhoudenConfig
from eboekhouden.exceptions import EBoekhoudenError

from eboekhouden_mcp.config import MCPConfig
from eboekhouden_mcp.tools import (
    ARCHIVE_TOOL_NAME,
    DESTRUCTIVE_TOOL_NAMES,
    WRITE_TOOL_NAMES,
    ToolRegistry,
    register_all_tools,
)

logger = logging.getLogger(__name__)

SERVER_INSTRUCTIONS = (
    "This server accesses live e-Boekhouden accounting data. Read-only tools are "
    "enabled by default. Never infer or expose credentials. Treat tool output as "
    "sensitive financial data. Before any write, delete, or archive action, explain "
    "the exact change and obtain explicit user confirmation. Prefer bounded searches "
    "and verify identifiers before actions."
)

WRITE_CONFIRMATION_FIELD = "confirm"


def _error_result(payload: dict) -> CallToolResult:
    return CallToolResult(
        content=[
            TextContent(
                type="text",
                text=json.dumps(payload, default=str, ensure_ascii=False),
            )
        ],
        isError=True,
    )


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
            secret_token=config.secret_token.get_secret_value(),
            api_url=config.api_url,
            source=config.source,
        )

    def tool_is_enabled(self, name: str) -> bool:
        """Return whether an operator enabled the requested capability."""
        if name == ARCHIVE_TOOL_NAME:
            return self.config.enable_write_tools and self.config.enable_archive_tool
        if name in WRITE_TOOL_NAMES:
            return self.config.enable_write_tools
        return True

    @asynccontextmanager
    async def get_client(self) -> AsyncIterator[EBoekhoudenClient]:
        """Get an authenticated e-Boekhouden client."""
        if self._client is None:
            self._client = EBoekhoudenClient(
                secret_token=self._sdk_config.secret_token.get_secret_value(),
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

    @asynccontextmanager
    async def lifespan(_: Server) -> AsyncIterator[None]:
        try:
            yield None
        finally:
            mcp_server.close()

    server = Server(
        config.server_name,
        version=config.server_version,
        instructions=SERVER_INSTRUCTIONS,
        lifespan=lifespan,
    )

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools."""
        tools = []
        for tool in mcp_server.registry.list_tools():
            if not mcp_server.tool_is_enabled(tool.name):
                continue
            is_write = tool.name in WRITE_TOOL_NAMES
            input_schema = tool.get_schema()
            if is_write:
                input_schema.setdefault("properties", {})[WRITE_CONFIRMATION_FIELD] = {
                    "type": "boolean",
                    "description": (
                        "Set to true only after the user explicitly confirms this exact "
                        "write action and its identifiers and values."
                    ),
                }
                required = input_schema.setdefault("required", [])
                if WRITE_CONFIRMATION_FIELD not in required:
                    required.append(WRITE_CONFIRMATION_FIELD)
            tools.append(
                Tool(
                    name=tool.name,
                    description=tool.description,
                    inputSchema=input_schema,
                    annotations=ToolAnnotations(
                        readOnlyHint=not is_write,
                        destructiveHint=tool.name in DESTRUCTIVE_TOOL_NAMES,
                        idempotentHint=not is_write,
                        openWorldHint=True,
                    ),
                )
            )
        return tools

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict
    ) -> list[TextContent] | CallToolResult:
        """Execute a tool by name."""
        tool = mcp_server.registry.get(name)
        if tool is None:
            return _error_result({"error": f"Unknown tool: {name}"})

        if not mcp_server.tool_is_enabled(name):
            setting = (
                "EBOEKHOUDEN_MCP_ENABLE_ARCHIVE_TOOL"
                if name == ARCHIVE_TOOL_NAME
                else "EBOEKHOUDEN_MCP_ENABLE_WRITE_TOOLS"
            )
            return _error_result(
                {
                    "error": "Tool disabled by server policy",
                    "hint": f"The operator must explicitly set {setting}=true.",
                }
            )

        execution_arguments = dict(arguments or {})
        if name in WRITE_TOOL_NAMES:
            if execution_arguments.get(WRITE_CONFIRMATION_FIELD) is not True:
                return _error_result(
                    {
                        "error": "Explicit write confirmation required",
                        "hint": (
                            "Confirm the exact action, identifiers, and values with "
                            "the user, then call again with confirm=true."
                        ),
                    }
                )
            execution_arguments.pop(WRITE_CONFIRMATION_FIELD)

        try:
            async with mcp_server.get_client() as client:
                result = await tool.execute(client, execution_arguments)
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(result, default=str, ensure_ascii=False),
                    )
                ]
        except EBoekhoudenError as e:
            return _error_result(
                {
                    "error": str(e),
                    "code": getattr(e, "code", None),
                    "details": getattr(e, "details", None),
                }
            )
        except Exception:
            logger.exception("Unexpected error executing tool %s", name)
            return _error_result(
                {
                    "error": "Unexpected server error",
                    "hint": "Check the MCP client logs for details.",
                }
            )

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
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-config",
        action="store_true",
        help="validate configuration without connecting to e-Boekhouden",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.2.0")
    args = parser.parse_args()

    try:
        config = MCPConfig()
    except ValidationError as exc:
        fields = ", ".join(
            ".".join(str(part) for part in error["loc"]) or "configuration"
            for error in exc.errors(include_url=False, include_input=False)
        )
        print(f"Invalid e-Boekhouden MCP configuration: {fields}", file=sys.stderr)
        print(
            "Set EBOEKHOUDEN_MCP_SECRET_TOKEN and review README.md.",
            file=sys.stderr,
        )
        raise SystemExit(2) from None

    if args.check_config:
        mode = "write-enabled" if config.enable_write_tools else "read-only"
        print(f"Configuration valid ({mode}; credentials redacted).")
        return

    logging.basicConfig(level=getattr(logging, config.log_level), stream=sys.stderr)
    asyncio.run(run_server(config))


if __name__ == "__main__":
    main()
