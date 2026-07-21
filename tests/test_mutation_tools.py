"""Tests for mutation MCP tools."""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

import pytest

from eboekhouden_mcp.tools.mutations import CreateMutationTool


def test_create_mutation_schema_advertises_type_as_string_enum():
    """The MCP schema should tell clients to send mutation type as a string."""
    schema = CreateMutationTool().get_schema()

    type_schema = schema["properties"]["type"]

    assert type_schema["type"] == "string"
    assert type_schema["enum"] == ["1", "2", "3", "4", "5", "6", "7"]


class _FakeMutations:
    def __init__(self) -> None:
        self.created = None

    def create(self, mutation):
        self.created = mutation
        return SimpleNamespace(id=9876)


class _FakeClient:
    def __init__(self) -> None:
        self.mutations = _FakeMutations()


@pytest.mark.asyncio
async def test_create_mutation_accepts_numeric_mcp_type_input():
    """Claude may send JSON numbers, but the SDK mutation enum uses string values."""
    client = _FakeClient()

    result = await CreateMutationTool().execute(
        client,
        {
            "type": 1,
            "date": "2026-07-05",
            "ledger_id": 1600,
            "rows": [
                {
                    "vat_code": "GEEN",
                    "amount": 12.34,
                    "vat_amount": 2.14,
                    "ledger_id": 8000,
                    "description": "Line",
                }
            ],
            "description": "Invoice",
            "invoice_number": "INV-1",
            "relation_id": 42,
            "term_of_payment": 14,
            "in_ex_vat": "EX",
        },
    )

    assert result == {"id": 9876}
    assert client.mutations.created is not None
    assert client.mutations.created.type == "1"
    assert client.mutations.created.rows[0].vat_amount == Decimal("2.14")


def test_create_mutation_schema_advertises_plain_rows_array():
    """The MCP schema should avoid anyOf for rows so Claude Desktop can validate it."""
    schema = CreateMutationTool().get_schema()

    rows_schema = schema["properties"]["rows"]
    type_schema = schema["properties"]["type"]
    term_schema = schema["properties"]["term_of_payment"]

    assert type_schema["type"] == "string"
    assert type_schema["enum"] == ["1", "2", "3", "4", "5", "6", "7"]
    assert term_schema["type"] == "integer"
    assert rows_schema["type"] == "array"
    assert rows_schema["items"]["type"] == "object"
    assert rows_schema["items"]["required"] == ["vat_code", "amount"]
    assert "anyOf" not in rows_schema
    assert schema["properties"]["rows_json"]["type"] == "string"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "rows",
    [
        '{"ledger_id": 32640553, "vat_code": "BU_EU_INK", "amount": 180.0}',
        '[{"ledger_id": 32640553, "vat_code": "BU_EU_INK", "amount": 180.0}]',
    ],
)
async def test_create_mutation_accepts_json_string_rows(rows):
    """The tool should normalize JSON-stringified row input before SDK validation."""
    client = _FakeClient()

    result = await CreateMutationTool().execute(
        client,
        {
            "type": "1",
            "date": "2026-04-05",
            "ledger_id": 32640540,
            "relation_id": "65776712",
            "in_ex_vat": "EX",
            "invoice_number": "5YR0KIVE-0003",
            "description": "Claude Max plan (20x) - april",
            "rows": rows,
        },
    )

    assert result == {"id": 9876}
    assert client.mutations.created.rows is not None
    assert len(client.mutations.created.rows) == 1
    assert client.mutations.created.rows[0].ledger_id == 32640553
    assert client.mutations.created.rows[0].vat_code == "BU_EU_INK"
    assert client.mutations.created.rows[0].amount == 180.0
    assert client.mutations.created.relation_id == 65776712
