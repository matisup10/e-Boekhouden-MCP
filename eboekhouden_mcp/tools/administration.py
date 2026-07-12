"""Administration tools for the e-Boekhouden MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import Field

from eboekhouden_mcp.tools.base import BaseTool, ToolSchema

if TYPE_CHECKING:
    from eboekhouden import EBoekhoudenClient


class ListAdministrationsInput(ToolSchema):
    """Input schema for list_administrations tool."""

    limit: int | None = Field(default=None, description="Number of items to retrieve (max 2000)")
    offset: int | None = Field(default=None, description="Number of items to skip")


class ListAdministrationsTool(BaseTool):
    """List all administrations managed by the authorized accountant."""

    name = "list_administrations"
    description = "List all administrations (bookkeeping accounts) managed by the authorized accountant"
    input_schema = ListAdministrationsInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        result = client.administrations.list(
            limit=arguments.get("limit"),
            offset=arguments.get("offset"),
        )
        return {
            "count": result.count,
            "items": [item.model_dump() for item in result.items],
        }


class ListLinkedAdministrationsInput(ToolSchema):
    """Input schema for list_linked_administrations tool."""

    limit: int | None = Field(default=None, description="Number of items to retrieve (max 2000)")
    offset: int | None = Field(default=None, description="Number of items to skip")


class ListLinkedAdministrationsTool(BaseTool):
    """List all administrations linked to the authorized administration."""

    name = "list_linked_administrations"
    description = "List all administrations linked to the current administration"
    input_schema = ListLinkedAdministrationsInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        result = client.administrations.list_linked(
            limit=arguments.get("limit"),
            offset=arguments.get("offset"),
        )
        return {
            "count": result.count,
            "items": [item.model_dump() for item in result.items],
        }
