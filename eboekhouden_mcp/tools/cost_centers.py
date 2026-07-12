"""Cost center tools for the e-Boekhouden MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import Field

from eboekhouden.models.cost_center import CreateCostCenter
from eboekhouden_mcp.tools.base import BaseTool, ToolSchema

if TYPE_CHECKING:
    from eboekhouden import EBoekhoudenClient


class ListCostCentersInput(ToolSchema):
    """Input schema for list_cost_centers tool."""

    limit: int | None = Field(default=None, description="Number of items to retrieve (max 2000)")
    offset: int | None = Field(default=None, description="Number of items to skip")
    parent_id: str | None = Field(default=None, description="Filter by parent cost center ID")
    description: str | None = Field(default=None, description="Filter by description")


class ListCostCentersTool(BaseTool):
    """List all cost centers."""

    name = "list_cost_centers"
    description = "List all cost centers (used for departmental or project accounting) with optional filters"
    input_schema = ListCostCentersInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        result = client.cost_centers.list(
            limit=arguments.get("limit"),
            offset=arguments.get("offset"),
            parent_id=arguments.get("parent_id"),
            description=arguments.get("description"),
        )
        return {
            "count": result.count,
            "items": [item.model_dump() for item in result.items],
        }


class GetCostCenterInput(ToolSchema):
    """Input schema for get_cost_center tool."""

    id: int = Field(description="Cost center ID")


class GetCostCenterTool(BaseTool):
    """Get a cost center by ID."""

    name = "get_cost_center"
    description = "Get full details of a cost center by ID, including the full path in the hierarchy"
    input_schema = GetCostCenterInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        cost_center = client.cost_centers.get(arguments["id"])
        return cost_center.model_dump()


class CreateCostCenterInput(ToolSchema):
    """Input schema for create_cost_center tool."""

    description: str = Field(description="Cost center description (max 50 chars)")
    parent_id: int | None = Field(default=None, description="Parent cost center ID for hierarchy")


class CreateCostCenterTool(BaseTool):
    """Create a new cost center."""

    name = "create_cost_center"
    description = "Create a new cost center for departmental or project accounting"
    input_schema = CreateCostCenterInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        cost_center_data = CreateCostCenter(
            description=arguments["description"],
            parent_id=arguments.get("parent_id"),
        )
        result = client.cost_centers.create(cost_center_data)
        return {"id": result.id, "active": result.active}


class DeleteCostCenterInput(ToolSchema):
    """Input schema for delete_cost_center tool."""

    id: int = Field(description="Cost center ID to delete")


class DeleteCostCenterTool(BaseTool):
    """Delete a cost center."""

    name = "delete_cost_center"
    description = "Delete a cost center by ID"
    input_schema = DeleteCostCenterInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        client.cost_centers.delete(arguments["id"])
        return {"success": True, "id": arguments["id"]}
