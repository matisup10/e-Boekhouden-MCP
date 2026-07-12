"""Template tools for the e-Boekhouden MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import Field

from eboekhouden_mcp.tools.base import BaseTool, ToolSchema

if TYPE_CHECKING:
    from eboekhouden import EBoekhoudenClient


class ListInvoiceTemplatesInput(ToolSchema):
    """Input schema for list_invoice_templates tool."""

    limit: int | None = Field(default=None, description="Number of items to retrieve (max 2000)")
    offset: int | None = Field(default=None, description="Number of items to skip")
    name: str | None = Field(default=None, description="Filter by template name")
    type: str | None = Field(default=None, description="Filter by type: 'E' for Editor, 'A' for Advanced")
    active: bool | None = Field(default=None, description="Filter by active status")


class ListInvoiceTemplatesTool(BaseTool):
    """List all invoice templates."""

    name = "list_invoice_templates"
    description = "List all invoice templates that can be used when creating invoices"
    input_schema = ListInvoiceTemplatesInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        result = client.invoice_templates.list(
            limit=arguments.get("limit"),
            offset=arguments.get("offset"),
            name=arguments.get("name"),
            type=arguments.get("type"),
            active=arguments.get("active"),
        )
        return {
            "count": result.count,
            "items": [item.model_dump() for item in result.items],
        }


class ListEmailTemplatesInput(ToolSchema):
    """Input schema for list_email_templates tool."""

    limit: int | None = Field(default=None, description="Number of items to retrieve (max 2000)")
    offset: int | None = Field(default=None, description="Number of items to skip")


class ListEmailTemplatesTool(BaseTool):
    """List all email templates."""

    name = "list_email_templates"
    description = "List all email templates used for sending invoices by email"
    input_schema = ListEmailTemplatesInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        result = client.email_templates.list(
            limit=arguments.get("limit"),
            offset=arguments.get("offset"),
        )
        return {
            "count": result.count,
            "items": [item.model_dump() for item in result.items],
        }
