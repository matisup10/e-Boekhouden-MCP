"""Tests for MCP tools."""

import pytest
from pydantic import ValidationError

from eboekhouden_mcp.tools import WRITE_TOOL_NAMES, ToolRegistry, register_all_tools
from eboekhouden_mcp.tools.base import BaseTool
from eboekhouden_mcp.tools.invoices import CreateInvoiceInput
from eboekhouden_mcp.tools.relations import ListRelationsInput


class TestToolRegistry:
    """Tests for the tool registry."""

    def test_register_and_get_tool(self):
        """Test registering and retrieving a tool."""
        registry = ToolRegistry()

        class TestTool(BaseTool):
            name = "test_tool"
            description = "A test tool"

            async def execute(self, client, arguments):
                return {"result": "ok"}

        tool = TestTool()
        registry.register(tool)

        assert registry.get("test_tool") == tool
        assert registry.get("nonexistent") is None

    def test_list_tools(self):
        """Test listing all registered tools."""
        registry = ToolRegistry()

        class Tool1(BaseTool):
            name = "tool1"
            description = "Tool 1"

            async def execute(self, client, arguments):
                return {}

        class Tool2(BaseTool):
            name = "tool2"
            description = "Tool 2"

            async def execute(self, client, arguments):
                return {}

        registry.register(Tool1())
        registry.register(Tool2())

        tools = registry.list_tools()
        assert len(tools) == 2

    def test_len_and_contains(self):
        """Test __len__ and __contains__ methods."""
        registry = ToolRegistry()

        class TestTool(BaseTool):
            name = "test"
            description = "Test"

            async def execute(self, client, arguments):
                return {}

        registry.register(TestTool())

        assert len(registry) == 1
        assert "test" in registry
        assert "other" not in registry


class TestRegisterAllTools:
    """Tests for registering all tools."""

    def test_registers_all_tools(self):
        """Test that all tools are registered (37 base + 12 power = 49)."""
        registry = ToolRegistry()
        register_all_tools(registry)

        # 37 base tools + 12 power tools
        assert len(registry) == 49

    def test_tool_categories(self):
        """Test that tools from all categories are registered."""
        registry = ToolRegistry()
        register_all_tools(registry)

        # Check for at least one tool from each category
        assert "list_relations" in registry
        assert "list_invoices" in registry
        assert "list_mutations" in registry
        assert "list_products" in registry
        assert "list_ledgers" in registry
        assert "list_cost_centers" in registry
        assert "list_members" in registry
        assert "list_administrations" in registry
        assert "list_invoice_templates" in registry
        assert "list_units" in registry
        assert "send_file_to_digital_archive" in registry

    def test_all_side_effect_named_tools_are_guarded(self):
        """Conventional write verbs must never bypass the server write policy."""
        registry = ToolRegistry()
        register_all_tools(registry)

        side_effect_tools = {
            tool.name
            for tool in registry.list_tools()
            if tool.name.startswith(("create_", "update_", "delete_", "send_"))
        }

        assert side_effect_tools == WRITE_TOOL_NAMES


class TestToolSchemas:
    """Tests for tool input schemas."""

    def test_get_schema(self):
        """Test that tools return valid JSON schemas."""
        registry = ToolRegistry()
        register_all_tools(registry)

        for tool in registry.list_tools():
            schema = tool.get_schema()
            assert isinstance(schema, dict)
            # Should not have title (MCP expects clean schema)
            assert "title" not in schema

    def test_paginated_inputs_enforce_api_bounds(self):
        schema = ListRelationsInput.model_json_schema()

        assert schema["properties"]["limit"]["anyOf"][0]["minimum"] == 1
        assert schema["properties"]["limit"]["anyOf"][0]["maximum"] == 2000
        assert schema["properties"]["offset"]["anyOf"][0]["minimum"] == 0

        with pytest.raises(ValidationError):
            ListRelationsInput(limit=2001)
        with pytest.raises(ValidationError):
            ListRelationsInput(offset=-1)

    def test_invoice_items_have_a_strict_nested_schema(self):
        schema = CreateInvoiceInput.model_json_schema()

        assert schema["properties"]["items"]["minItems"] == 1
        assert schema["properties"]["items"]["maxItems"] == 500
        assert schema["$defs"]["InvoiceItemInput"]["additionalProperties"] is False

        with pytest.raises(ValidationError):
            CreateInvoiceInput(
                relation_id=1,
                term_of_payment=14,
                template_id=1,
                items=[{"description": "Missing required line fields"}],
            )

    def test_tool_inputs_reject_unknown_fields(self):
        with pytest.raises(ValidationError):
            ListRelationsInput(unexpected=True)
