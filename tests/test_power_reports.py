"""Tests for the power report/aggregate tools."""

from __future__ import annotations

from eboekhouden.models.ledger import LedgerBalance, LedgerListItem
from eboekhouden.models.mutation import (
    Mutation,
    MutationListItem,
    MutationRow,
    OutstandingInvoice,
    VatAmount,
)
from eboekhouden_mcp.tools.power.reports import (
    ArApAgingTool,
    BalanceSheetTool,
    LedgerTransactionsTool,
    ProfitLossTool,
    TrialBalanceTool,
    VatSummaryTool,
)


class _FakeLedgers:
    def __init__(self, ledgers, balances):
        self._ledgers = ledgers
        self._balances = balances
        self.balance_calls: list[dict] = []

    def iter_all(self, limit=100, **kwargs):
        return iter(self._ledgers)

    def get_balance(self, id, *, cost_center_id=None, from_date=None, to_date=None):
        self.balance_calls.append(
            {"id": id, "cc": cost_center_id, "from": from_date, "to": to_date}
        )
        return self._balances[id]


class _FakeMutations:
    def __init__(self, list_items=None, details=None, outstanding=None):
        self._list_items = list_items or []
        self._details = details or {}
        self._outstanding = outstanding or {}

    def list(self, **kwargs):
        from types import SimpleNamespace

        return SimpleNamespace(
            items=list(self._list_items), count=len(self._list_items)
        )

    def get(self, id):
        return self._details[id]

    def iter_outstanding(self, cred_deb, limit=100, **kwargs):
        return iter(self._outstanding.get(cred_deb, []))


class _FakeClient:
    def __init__(self, ledgers=None, mutations=None):
        self.ledgers = ledgers
        self.mutations = mutations


def _ledgers_client():
    ledgers = [
        LedgerListItem(id=8000, code="8000", description="Sales", category="VW"),
        LedgerListItem(id=4000, code="4000", description="Office costs", category="VW"),
        LedgerListItem(id=1000, code="1000", description="Bank", category="BAL"),
    ]
    balances = {
        8000: LedgerBalance(code="8000", type="VW", balance=-1000),
        4000: LedgerBalance(code="4000", type="VW", balance=300),
        1000: LedgerBalance(code="1000", type="BAL", balance=700),
    }
    return _FakeClient(ledgers=_FakeLedgers(ledgers, balances))


# --------------------------------------------------------------------------- #
# trial balance / P&L / balance sheet
# --------------------------------------------------------------------------- #


async def test_trial_balance_groups_by_category_with_totals():
    client = _ledgers_client()
    result = await TrialBalanceTool().execute(
        client, {"from_date": "2026-01-01", "to_date": "2026-12-31"}
    )

    assert result["grand_total"] == 0.0
    vw = result["by_category"]["VW"]
    assert vw["total"] == -700.0
    assert client.ledgers.balance_calls[0]["from"] is not None  # date range forwarded


async def test_trial_balance_markdown_format():
    client = _ledgers_client()
    result = await TrialBalanceTool().execute(client, {"format": "markdown"})
    assert "markdown" in result
    assert "| code |" in result["markdown"]


async def test_profit_loss_splits_revenue_and_expense():
    client = _ledgers_client()
    result = await ProfitLossTool().execute(client, {})
    assert result["revenue_total"] == 1000.0
    assert result["expense_total"] == 300.0
    assert result["net_result"] == 700.0


async def test_balance_sheet_only_bal_accounts():
    client = _ledgers_client()
    result = await BalanceSheetTool().execute(client, {})
    assert result["assets_total"] == 700.0
    assert result["liabilities_total"] == 0.0
    codes = {row["code"] for row in result["rows"]}
    assert codes == {"1000"}  # VW accounts excluded


# --------------------------------------------------------------------------- #
# VAT summary
# --------------------------------------------------------------------------- #


async def test_vat_summary_sums_by_code():
    details = {
        1: Mutation(
            id=1,
            type="2",
            date="2026-03-01",
            ledgerId=8000,
            vat=[VatAmount(vatCode="HOOG_VERK_21", amount=21)],
        ),
        2: Mutation(
            id=2,
            type="1",
            date="2026-03-02",
            ledgerId=4000,
            vat=[VatAmount(vatCode="HOOG_INK_21", amount=10)],
        ),
    }
    list_items = [
        MutationListItem(id=1, type="2", date="2026-03-01", ledgerId=8000, amount=121),
        MutationListItem(id=2, type="1", date="2026-03-02", ledgerId=4000, amount=48),
    ]
    client = _FakeClient(
        mutations=_FakeMutations(list_items=list_items, details=details)
    )

    result = await VatSummaryTool().execute(
        client, {"date_from": "2026-01-01", "date_to": "2026-03-31"}
    )

    by_code = {row["vat_code"]: row["amount"] for row in result["by_code"]}
    assert by_code == {"HOOG_VERK_21": 21.0, "HOOG_INK_21": 10.0}
    assert result["total_vat"] == 31.0
    assert result["mutations_scanned"] == 2


# --------------------------------------------------------------------------- #
# AR/AP aging
# --------------------------------------------------------------------------- #


async def test_ar_ap_aging_buckets_by_age():
    outstanding = {
        "D": [
            OutstandingInvoice(
                date="2026-06-01",
                mutationId=1,
                relationId=5,
                company="Acme",
                totalAmount=100,
                paidAmount=0,
                outstandingAmount=100,
            ),
            OutstandingInvoice(
                date="2026-07-10",
                mutationId=2,
                relationId=6,
                company="Beta",
                totalAmount=50,
                paidAmount=0,
                outstandingAmount=50,
            ),
        ]
    }
    client = _FakeClient(mutations=_FakeMutations(outstanding=outstanding))

    result = await ArApAgingTool().execute(
        client, {"cred_deb": "D", "reference_date": "2026-07-12"}
    )

    debtors = result["debtors"]
    assert debtors["total"] == 150.0
    # Acme invoice is 41 days old -> 31-60 bucket; Beta is 2 days -> 0-30
    assert debtors["bucket_totals"]["31-60"] == 100.0
    assert debtors["bucket_totals"]["0-30"] == 50.0


# --------------------------------------------------------------------------- #
# ledger transactions
# --------------------------------------------------------------------------- #


async def test_ledger_transactions_running_total():
    list_items = [
        MutationListItem(id=1, type="2", date="2026-01-05", ledgerId=8000, amount=300),
        MutationListItem(id=2, type="2", date="2026-01-06", ledgerId=9999, amount=10),
    ]
    details = {
        1: Mutation(
            id=1,
            type="2",
            date="2026-01-05",
            ledgerId=8000,
            rows=[MutationRow(ledgerId=4000, amount=300)],
        ),
        2: Mutation(
            id=2,
            type="2",
            date="2026-01-06",
            ledgerId=9999,
            rows=[MutationRow(ledgerId=5000, amount=10)],
        ),
    }
    client = _FakeClient(
        mutations=_FakeMutations(list_items=list_items, details=details)
    )

    result = await LedgerTransactionsTool().execute(client, {"ledger_id": 4000})

    assert result["count"] == 1
    assert result["total"] == 300.0
    assert result["items"][0]["mutation_id"] == 1
