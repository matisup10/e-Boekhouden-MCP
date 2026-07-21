"""Tests for the power batch-detail tools."""

from __future__ import annotations

from eboekhouden.models.invoice import Invoice, InvoiceItem
from eboekhouden.models.mutation import Mutation, MutationRow
from eboekhouden.models.relation import Relation
from eboekhouden_mcp.tools.power.batch import (
    GetInvoicesBatchTool,
    GetMutationsBatchTool,
    GetRelationsBatchTool,
)


class _FakeService:
    def __init__(self, details):
        self._details = details
        self.got_ids: list[int] = []

    def get(self, id):
        self.got_ids.append(id)
        return self._details[id]


class _FakeClient:
    def __init__(self, relations=None, mutations=None, invoices=None):
        self.relations = relations
        self.mutations = mutations
        self.invoices = invoices


async def test_get_mutations_batch_returns_full_detail():
    mutations = _FakeService(
        {
            10: Mutation(
                id=10,
                type="2",
                date="2026-01-05",
                ledgerId=8000,
                rows=[MutationRow(ledgerId=4000, amount=50)],
            ),
            11: Mutation(
                id=11,
                type="2",
                date="2026-01-06",
                ledgerId=8000,
                rows=[MutationRow(ledgerId=4000, amount=75)],
            ),
        }
    )
    client = _FakeClient(mutations=mutations)

    result = await GetMutationsBatchTool().execute(client, {"ids": [10, 11]})

    assert result["count"] == 2
    assert mutations.got_ids == [10, 11]
    assert result["items"][0]["rows"][0]["amount"] == 50


async def test_get_mutations_batch_respects_cap():
    details = {
        i: Mutation(id=i, type="2", date="2026-01-05", ledgerId=8000)
        for i in range(1, 6)
    }
    mutations = _FakeService(details)
    client = _FakeClient(mutations=mutations)

    result = await GetMutationsBatchTool().execute(
        client, {"ids": [1, 2, 3, 4, 5], "max_details": 2}
    )

    assert result["count"] == 2
    assert result["truncated"] is True
    assert mutations.got_ids == [1, 2]  # cap stops extra fetches


async def test_get_mutations_batch_empty_ids_errors():
    client = _FakeClient(mutations=_FakeService({}))
    result = await GetMutationsBatchTool().execute(client, {"ids": []})
    assert "error" in result


async def test_get_mutations_batch_accepts_json_string_ids():
    mutations = _FakeService(
        {10: Mutation(id=10, type="2", date="2026-01-05", ledgerId=8000)}
    )
    client = _FakeClient(mutations=mutations)

    result = await GetMutationsBatchTool().execute(client, {"ids": "[10]"})
    assert result["count"] == 1
    assert mutations.got_ids == [10]


async def test_get_relations_batch_returns_names():
    relations = _FakeService(
        {1: Relation(id=1, name="Acme BV"), 2: Relation(id=2, name="Beta NV")}
    )
    client = _FakeClient(relations=relations)

    result = await GetRelationsBatchTool().execute(client, {"ids": [1, 2]})
    assert {item["name"] for item in result["items"]} == {"Acme BV", "Beta NV"}


async def test_get_invoices_batch_returns_line_items():
    invoices = _FakeService(
        {
            7: Invoice(
                id=7,
                invoiceNumber="INV-7",
                relationId=5,
                date="2026-02-01",
                termOfPayment=14,
                templateId=1,
                totalExcl=100,
                totalAmount=121,
                vatAmount=21,
                items=[
                    InvoiceItem(
                        description="Widget", vatCode="HOOG_VERK_21", ledgerId=8000
                    )
                ],
            )
        }
    )
    client = _FakeClient(invoices=invoices)

    result = await GetInvoicesBatchTool().execute(client, {"ids": [7]})
    assert result["items"][0]["items"][0]["description"] == "Widget"


def test_batch_schema_advertises_integer_array_ids():
    schema = GetMutationsBatchTool().get_schema()
    ids_schema = schema["properties"]["ids"]
    assert ids_schema["type"] == "array"
    assert ids_schema["items"]["type"] == "integer"
    assert "anyOf" not in ids_schema
