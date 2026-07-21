"""Base tool class and registry for MCP tools."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from eboekhouden import EBoekhoudenClient


class ToolSchema(BaseModel):
    """Schema for tool input parameters."""

    model_config = ConfigDict(extra="forbid")


class PaginatedInput(ToolSchema):
    """Shared API pagination constraints."""

    limit: int | None = Field(
        default=None,
        ge=1,
        le=2000,
        description="Number of items to retrieve (1-2000)",
    )
    offset: int | None = Field(
        default=None,
        ge=0,
        description="Number of items to skip (0 or greater)",
    )


class BaseTool(ABC):
    """Base class for all MCP tools."""

    name: str
    description: str
    input_schema: type[ToolSchema] = ToolSchema

    @abstractmethod
    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute the tool with the given arguments.

        Args:
            client: The authenticated e-Boekhouden client
            arguments: The tool arguments as a dictionary

        Returns:
            The tool result as a dictionary
        """
        pass

    def get_schema(self) -> dict[str, Any]:
        """Get the JSON schema for this tool's input parameters."""
        schema = self.input_schema.model_json_schema()
        # Remove title and description from schema root (MCP expects clean schema)
        schema.pop("title", None)
        return schema


class ToolRegistry:
    """Registry for managing MCP tools."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool with the registry."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[BaseTool]:
        """List all registered tools."""
        return list(self._tools.values())

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools
