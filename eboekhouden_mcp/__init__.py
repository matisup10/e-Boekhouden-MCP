"""MCP server for the e-Boekhouden Dutch accounting API."""

from eboekhouden_mcp.config import MCPConfig
from eboekhouden_mcp.server import create_server

__version__ = "0.2.0"
__all__ = ["MCPConfig", "create_server"]
