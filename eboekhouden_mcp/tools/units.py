"""Unit tools for the e-Boekhouden MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from eboekhouden_mcp.tools.base import BaseTool, PaginatedInput

if TYPE_CHECKING:
    from eboekhouden import EBoekhoudenClient


class ListUnitsInput(PaginatedInput):
    """Input schema for list_units tool."""


class ListUnitsTool(BaseTool):
    """List all units of measurement."""

    name = "list_units"
    description = "List all units of measurement (e.g., pieces, hours, kg) used for products and invoice line items"
    input_schema = ListUnitsInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        result = client.units.list(
            limit=arguments.get("limit"),
            offset=arguments.get("offset"),
        )
        return {
            "count": result.count,
            "items": [item.model_dump() for item in result.items],
        }
