"""Tests for the power search tools."""

from __future__ import annotations

from types import SimpleNamespace

from eboekhouden.filters import Filter
from eboekhouden.models.invoice import Invoice, InvoiceItem, InvoiceListItem
from eboekhouden.models.mutation import Mutation, MutationListItem, MutationRow
from eboekhouden.models.relation import Relation, RelationListItem
from eboekhouden_mcp.tools.power.search import (
    SearchInvoicesTool,
    SearchMutationsTool,
    SearchRelationsTool,
)


class _FakeService:
    def __init__(self, list_items, details=None):
        self._list_items = list_items
        self._details = details or {}
        self.list_kwargs = None
        self.got_ids: list[int] = []

    def list(self, **kwargs):
        self.list_kwargs = kwargs
        return SimpleNamespace(items=list(self._list_items), count=len(self._list_items))

    def get(self, id):
        self.got_ids.append(id)
        return self._details[id]


class _FakeClient:
    def __init__(self, relations=None, mutations=None, invoices=None):
        self.relations = relations
        self.mutations = mutations
        self.invoices = invoices


# --------------------------------------------------------------------------- #
# search_relations
# --------------------------------------------------------------------------- #


async def test_search_relations_hydrates_full_detail_by_default():
    relations = _FakeService(
        [RelationListItem(id=1, type="B", code="C1"), RelationListItem(id=2, type="B", code="C2")],
        {
            1: Relation(id=1, name="Acme BV", city="Amsterdam"),
            2: Relation(id=2, name="Acme Holding", city="Utrecht"),
        },
    )
    client = _FakeClient(relations=relations)

    result = await SearchRelationsTool().execute(client, {"name": "acme"})

    # name filter is sent server-side as a like filter
    assert isinstance(relations.list_kwargs["name"], Filter)
    assert relations.list_kwargs["name"].operator == "like"
    # both matches hydrated -> names present (the whole point)
    assert result["count"] == 2
    assert {item["name"] for item in result["items"]} == {"Acme BV", "Acme Holding"}


async def test_search_relations_without_hydrate_returns_list_fields_only():
    relations = _FakeService(
        [RelationListItem(id=1, type="B", code="C1")],
        {1: Relation(id=1, name="Acme BV")},
    )
    client = _FakeClient(relations=relations)

    result = await SearchRelationsTool().execute(client, {"name": "acme", "hydrate": False})

    assert relations.got_ids == []  # no per-id fetches
    assert "name" not in result["items"][0]


# --------------------------------------------------------------------------- #
# search_mutations
# --------------------------------------------------------------------------- #


def _mut_item(id, amount, ledger_id=8000):
    return MutationListItem(id=id, type="2", date="2026-01-05", ledgerId=ledger_id, amount=amount)


async def test_search_mutations_filters_by_relation_via_hydration():
    mutations = _FakeService(
        [_mut_item(10, 100), _mut_item(11, 200), _mut_item(12, 300)],
        {
            10: Mutation(id=10, type="2", date="2026-01-05", ledgerId=8000, relationId=42),
            11: Mutation(id=11, type="2", date="2026-01-06", ledgerId=8000, relationId=99),
            12: Mutation(id=12, type="2", date="2026-01-07", ledgerId=8000, relationId=42),
        },
    )
    client = _FakeClient(mutations=mutations)

    result = await SearchMutationsTool().execute(client, {"relation_id": 42})

    assert result["count"] == 2
    assert {item["id"] for item in result["items"]} == {10, 12}


async def test_search_mutations_amount_prefilter_without_hydration():
    mutations = _FakeService([_mut_item(10, 100), _mut_item(11, 200), _mut_item(12, 300)])
    client = _FakeClient(mutations=mutations)

    result = await SearchMutationsTool().execute(
        client, {"amount_min": 150, "amount_max": 250, "hydrate": False}
    )

    assert mutations.got_ids == []
    assert result["count"] == 1
    assert result["items"][0]["id"] == 11


async def test_search_mutations_respects_max_details_cap():
    items = [_mut_item(i, 100) for i in range(20, 26)]
    details = {i: Mutation(id=i, type="2", date="2026-01-05", ledgerId=8000, relationId=7) for i in range(20, 26)}
    mutations = _FakeService(items, details)
    client = _FakeClient(mutations=mutations)

    result = await SearchMutationsTool().execute(client, {"relation_id": 7, "max_details": 2})

    assert result["count"] == 2
    assert result["truncated"] is True
    assert "hint" in result


async def test_search_mutations_matches_ledger_on_row_level():
    mutations = _FakeService(
        [_mut_item(10, 100, ledger_id=8000)],
        {
            10: Mutation(
                id=10,
                type="2",
                date="2026-01-05",
                ledgerId=8000,
                rows=[MutationRow(ledgerId=4500, amount=100)],
            )
        },
    )
    client = _FakeClient(mutations=mutations)

    # 4500 only appears on a row, not the header
    result = await SearchMutationsTool().execute(client, {"ledger_id": 4500})
    assert result["count"] == 1


# --------------------------------------------------------------------------- #
# search_invoices
# --------------------------------------------------------------------------- #


def _inv_item(id, total):
    return InvoiceListItem(
        id=id,
        invoiceNumber=f"INV-{id}",
        relationId=5,
        date="2026-02-01",
        totalExcl=total,
        totalAmount=total,
        vatAmount=0,
        termOfPayment=14,
        templateId=1,
    )


async def test_search_invoices_amount_filter_on_total():
    invoices = _FakeService([_inv_item(1, 100), _inv_item(2, 500)])
    client = _FakeClient(invoices=invoices)

    result = await SearchInvoicesTool().execute(client, {"amount_min": 200})

    assert result["count"] == 1
    assert result["items"][0]["invoice_number"] == "INV-2"


async def test_search_invoices_hydrate_adds_line_items():
    invoices = _FakeService(
        [_inv_item(1, 100)],
        {
            1: Invoice(
                id=1,
                invoiceNumber="INV-1",
                relationId=5,
                date="2026-02-01",
                termOfPayment=14,
                templateId=1,
                totalExcl=100,
                totalAmount=100,
                vatAmount=0,
                items=[InvoiceItem(description="Widget", vatCode="HOOG_VERK_21", ledgerId=8000)],
            )
        },
    )
    client = _FakeClient(invoices=invoices)

    result = await SearchInvoicesTool().execute(client, {"hydrate": True})

    assert invoices.got_ids == [1]
    assert result["items"][0]["items"][0]["description"] == "Widget"
