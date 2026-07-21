"""Administration tools for the e-Boekhouden MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from eboekhouden_mcp.tools.base import BaseTool, PaginatedInput

if TYPE_CHECKING:
    from eboekhouden import EBoekhoudenClient


class ListAdministrationsInput(PaginatedInput):
    """Input schema for list_administrations tool."""


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


class ListLinkedAdministrationsInput(PaginatedInput):
    """Input schema for list_linked_administrations tool."""


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
