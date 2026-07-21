"""MCP tools for e-Boekhouden operations."""

from eboekhouden_mcp.tools.base import BaseTool, ToolRegistry
from eboekhouden_mcp.tools.relations import (
    ListRelationsTool,
    GetRelationTool,
    CreateRelationTool,
    UpdateRelationTool,
    DeleteRelationTool,
)
from eboekhouden_mcp.tools.invoices import (
    ListInvoicesTool,
    GetInvoiceTool,
    CreateInvoiceTool,
)
from eboekhouden_mcp.tools.mutations import (
    ListMutationsTool,
    GetMutationTool,
    CreateMutationTool,
    ListOutstandingInvoicesTool,
)
from eboekhouden_mcp.tools.products import (
    ListProductsTool,
    GetProductTool,
    CreateProductTool,
    UpdateProductTool,
    DeleteProductTool,
    ListProductGroupsTool,
)
from eboekhouden_mcp.tools.ledgers import (
    ListLedgersTool,
    GetLedgerTool,
    CreateLedgerTool,
    UpdateLedgerTool,
    GetLedgerBalanceTool,
)
from eboekhouden_mcp.tools.cost_centers import (
    ListCostCentersTool,
    GetCostCenterTool,
    CreateCostCenterTool,
    DeleteCostCenterTool,
)
from eboekhouden_mcp.tools.members import (
    ListMembersTool,
    GetMemberTool,
    CreateMemberTool,
    DeleteMemberTool,
)
from eboekhouden_mcp.tools.administration import (
    ListAdministrationsTool,
    ListLinkedAdministrationsTool,
)
from eboekhouden_mcp.tools.archive import SendFileToDigitalArchiveTool
from eboekhouden_mcp.tools.templates import (
    ListInvoiceTemplatesTool,
    ListEmailTemplatesTool,
)
from eboekhouden_mcp.tools.units import ListUnitsTool
from eboekhouden_mcp.tools.power import register_power_tools


WRITE_TOOL_NAMES = frozenset(
    {
        "create_relation",
        "update_relation",
        "delete_relation",
        "create_invoice",
        "create_mutation",
        "create_product",
        "update_product",
        "delete_product",
        "create_ledger",
        "update_ledger",
        "create_cost_center",
        "delete_cost_center",
        "create_member",
        "delete_member",
        "send_file_to_digital_archive",
    }
)

DESTRUCTIVE_TOOL_NAMES = frozenset(
    {
        "delete_relation",
        "delete_product",
        "delete_cost_center",
        "delete_member",
    }
)

ARCHIVE_TOOL_NAME = "send_file_to_digital_archive"


def register_all_tools(registry: ToolRegistry) -> None:
    """Register all available tools with the registry."""
    # Relations (5 tools)
    registry.register(ListRelationsTool())
    registry.register(GetRelationTool())
    registry.register(CreateRelationTool())
    registry.register(UpdateRelationTool())
    registry.register(DeleteRelationTool())

    # Invoices (3 tools)
    registry.register(ListInvoicesTool())
    registry.register(GetInvoiceTool())
    registry.register(CreateInvoiceTool())

    # Mutations (4 tools)
    registry.register(ListMutationsTool())
    registry.register(GetMutationTool())
    registry.register(CreateMutationTool())
    registry.register(ListOutstandingInvoicesTool())

    # Products (6 tools)
    registry.register(ListProductsTool())
    registry.register(GetProductTool())
    registry.register(CreateProductTool())
    registry.register(UpdateProductTool())
    registry.register(DeleteProductTool())
    registry.register(ListProductGroupsTool())

    # Ledgers (5 tools)
    registry.register(ListLedgersTool())
    registry.register(GetLedgerTool())
    registry.register(CreateLedgerTool())
    registry.register(UpdateLedgerTool())
    registry.register(GetLedgerBalanceTool())

    # Cost Centers (4 tools)
    registry.register(ListCostCentersTool())
    registry.register(GetCostCenterTool())
    registry.register(CreateCostCenterTool())
    registry.register(DeleteCostCenterTool())

    # Members (4 tools)
    registry.register(ListMembersTool())
    registry.register(GetMemberTool())
    registry.register(CreateMemberTool())
    registry.register(DeleteMemberTool())

    # Administration (2 tools)
    registry.register(ListAdministrationsTool())
    registry.register(ListLinkedAdministrationsTool())

    # Templates (2 tools)
    registry.register(ListInvoiceTemplatesTool())
    registry.register(ListEmailTemplatesTool())

    # Units (1 tool)
    registry.register(ListUnitsTool())

    # Digital archive (1 tool)
    registry.register(SendFileToDigitalArchiveTool())

    # Power tools (12): enriched search, batch detail, reports
    register_power_tools(registry)


__all__ = [
    "BaseTool",
    "ToolRegistry",
    "register_all_tools",
    "register_power_tools",
    "WRITE_TOOL_NAMES",
    "DESTRUCTIVE_TOOL_NAMES",
    "ARCHIVE_TOOL_NAME",
]
