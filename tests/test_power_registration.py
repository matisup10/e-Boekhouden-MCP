"""The power tools must be wired into the server registry with valid schemas."""

from __future__ import annotations

from eboekhouden_mcp.tools import ToolRegistry, register_all_tools

_POWER_TOOLS = {
    "search_relations",
    "search_mutations",
    "search_invoices",
    "get_mutations_batch",
    "get_relations_batch",
    "get_invoices_batch",
    "get_trial_balance",
    "get_profit_loss",
    "get_balance_sheet",
    "get_vat_summary",
    "get_ar_ap_aging",
    "get_ledger_transactions",
}


def test_all_power_tools_registered():
    registry = ToolRegistry()
    register_all_tools(registry)
    registered = {tool.name for tool in registry.list_tools()}
    assert _POWER_TOOLS <= registered


def test_power_tool_schemas_are_valid_objects():
    registry = ToolRegistry()
    register_all_tools(registry)
    for tool in registry.list_tools():
        if tool.name in _POWER_TOOLS:
            schema = tool.get_schema()
            assert isinstance(schema, dict)
            assert schema.get("type") == "object"
            assert "properties" in schema
