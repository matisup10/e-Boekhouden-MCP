"""Power tools: enriched search, batch detail, and client-side reports.

Self-contained add-on layer for the e-Boekhouden MCP server. Everything here is
additive — the base tools are untouched. Register the whole layer with a single
call to :func:`register_power_tools`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eboekhouden_mcp.tools.base import ToolRegistry


def register_power_tools(registry: "ToolRegistry") -> None:
    """Register every power tool with the given registry."""
    from eboekhouden_mcp.tools.power.search import (
        SearchInvoicesTool,
        SearchMutationsTool,
        SearchRelationsTool,
    )
    from eboekhouden_mcp.tools.power.batch import (
        GetInvoicesBatchTool,
        GetMutationsBatchTool,
        GetRelationsBatchTool,
    )
    from eboekhouden_mcp.tools.power.reports import (
        ArApAgingTool,
        BalanceSheetTool,
        LedgerTransactionsTool,
        ProfitLossTool,
        TrialBalanceTool,
        VatSummaryTool,
    )

    # Enriched search
    registry.register(SearchRelationsTool())
    registry.register(SearchMutationsTool())
    registry.register(SearchInvoicesTool())

    # Batch detail
    registry.register(GetMutationsBatchTool())
    registry.register(GetRelationsBatchTool())
    registry.register(GetInvoicesBatchTool())

    # Reports / aggregates
    registry.register(TrialBalanceTool())
    registry.register(ProfitLossTool())
    registry.register(BalanceSheetTool())
    registry.register(VatSummaryTool())
    registry.register(ArApAgingTool())
    registry.register(LedgerTransactionsTool())


__all__ = ["register_power_tools"]
