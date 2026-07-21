"""Report / aggregate tools built from client-side rollups.

The API exposes only per-ledger balance and outstanding-invoice endpoints, so
trial balance, P&L, balance sheet, VAT summary and AR/AP aging are all computed
here by iterating the primitives. Each of these replaces many individual tool
calls with a single one.
"""

from __future__ import annotations

import datetime
from collections import defaultdict
from typing import TYPE_CHECKING, Any

from pydantic import Field

from eboekhouden_mcp.tools.base import BaseTool, ToolSchema
from eboekhouden_mcp.tools.power._helpers import (
    compact,
    parse_date,
    range_date_filter,
    round2,
    to_markdown_table,
)

if TYPE_CHECKING:
    from eboekhouden import EBoekhoudenClient

_SCAN_LIMIT_DEFAULT = 500
_MAX_DETAILS_DEFAULT = 50


# Local date parser (kept here so _helpers stays filter-focused).
def _pdate(value: Any) -> datetime.date | None:
    return parse_date(value)


# --------------------------------------------------------------------------- #
# ledger balance rollups: trial balance, P&L, balance sheet
# --------------------------------------------------------------------------- #


def _ledger_balances(
    client: "EBoekhoudenClient",
    *,
    from_date: datetime.date | None,
    to_date: datetime.date | None,
    cost_center_id: int | None,
    categories: set[str] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for ledger in client.ledgers.iter_all(limit=2000):
        if categories is not None and ledger.category not in categories:
            continue
        balance = client.ledgers.get_balance(
            ledger.id,
            cost_center_id=cost_center_id,
            from_date=from_date,
            to_date=to_date,
        )
        rows.append(
            {
                "ledger_id": ledger.id,
                "code": ledger.code,
                "description": ledger.description,
                "category": ledger.category,
                "balance": round2(balance.balance),
            }
        )
    return rows


class _PeriodInput(ToolSchema):
    from_date: str | None = Field(default=None, description="Period start (YYYY-MM-DD)")
    to_date: str | None = Field(default=None, description="Period end (YYYY-MM-DD)")
    cost_center_id: int | None = Field(
        default=None, description="Restrict to a single cost center"
    )
    format: str | None = Field(
        default="json", description="'json' (default) or 'markdown'"
    )


class TrialBalanceInput(_PeriodInput):
    category: str | None = Field(
        default=None,
        description="Restrict to one ledger category (e.g. BAL, VW, FIN, DEB, CRED)",
    )


class TrialBalanceTool(BaseTool):
    """Trial balance across all ledgers, grouped by category."""

    name = "get_trial_balance"
    description = (
        "Trial balance: the balance of every ledger over an optional period, grouped by category "
        "(BAL/VW/etc.) with subtotals and a grand total. One call instead of get_ledger_balance per account."
    )
    input_schema = TrialBalanceInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        category = arguments.get("category")
        categories = {category} if category else None
        rows = _ledger_balances(
            client,
            from_date=_pdate(arguments.get("from_date")),
            to_date=_pdate(arguments.get("to_date")),
            cost_center_id=arguments.get("cost_center_id"),
            categories=categories,
        )

        by_category: dict[str, Any] = {}
        for row in rows:
            bucket = by_category.setdefault(
                row["category"], {"total": 0.0, "accounts": []}
            )
            bucket["accounts"].append(row)
            bucket["total"] = round2(bucket["total"] + row["balance"])

        result: dict[str, Any] = {
            "from_date": arguments.get("from_date"),
            "to_date": arguments.get("to_date"),
            "account_count": len(rows),
            "by_category": by_category,
            "grand_total": round2(sum(row["balance"] for row in rows)),
        }
        if arguments.get("format") == "markdown":
            result["markdown"] = to_markdown_table(
                rows, ["code", "description", "category", "balance"]
            )
        return result


class ProfitLossTool(BaseTool):
    """Profit & loss over the VW (result) ledgers."""

    name = "get_profit_loss"
    description = (
        "Profit & loss over the period: revenue vs expense across VW ledgers and the net result. "
        "Convention: positive balance = debit (expense), negative = credit (revenue)."
    )
    input_schema = _PeriodInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        rows = _ledger_balances(
            client,
            from_date=_pdate(arguments.get("from_date")),
            to_date=_pdate(arguments.get("to_date")),
            cost_center_id=arguments.get("cost_center_id"),
            categories={"VW"},
        )
        expenses = [r for r in rows if r["balance"] > 0]
        revenue = [r for r in rows if r["balance"] < 0]
        expense_total = round2(sum(r["balance"] for r in expenses))
        revenue_total = round2(-sum(r["balance"] for r in revenue))

        result: dict[str, Any] = {
            "from_date": arguments.get("from_date"),
            "to_date": arguments.get("to_date"),
            "revenue_total": revenue_total,
            "expense_total": expense_total,
            "net_result": round2(revenue_total - expense_total),
            "revenue": revenue,
            "expenses": expenses,
        }
        if arguments.get("format") == "markdown":
            result["markdown"] = to_markdown_table(
                rows, ["code", "description", "balance"]
            )
        return result


class BalanceSheetTool(BaseTool):
    """Balance sheet over the BAL ledgers."""

    name = "get_balance_sheet"
    description = (
        "Balance sheet: assets vs liabilities across BAL ledgers with totals. "
        "Convention: positive balance = debit (asset), negative = credit (liability/equity)."
    )
    input_schema = _PeriodInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        rows = _ledger_balances(
            client,
            from_date=_pdate(arguments.get("from_date")),
            to_date=_pdate(arguments.get("to_date")),
            cost_center_id=arguments.get("cost_center_id"),
            categories={"BAL"},
        )
        assets = [r for r in rows if r["balance"] > 0]
        liabilities = [r for r in rows if r["balance"] < 0]
        assets_total = round2(sum(r["balance"] for r in assets))
        liabilities_total = round2(-sum(r["balance"] for r in liabilities))

        result: dict[str, Any] = {
            "as_of": arguments.get("to_date"),
            "assets_total": assets_total,
            "liabilities_total": liabilities_total,
            "difference": round2(assets_total - liabilities_total),
            "rows": rows,
        }
        if arguments.get("format") == "markdown":
            result["markdown"] = to_markdown_table(
                rows, ["code", "description", "balance"]
            )
        return result


# --------------------------------------------------------------------------- #
# VAT summary
# --------------------------------------------------------------------------- #


class VatSummaryInput(ToolSchema):
    date_from: str | None = Field(default=None, description="Period start (YYYY-MM-DD)")
    date_to: str | None = Field(default=None, description="Period end (YYYY-MM-DD)")
    max_details: int = Field(
        default=_MAX_DETAILS_DEFAULT,
        description="Max mutations to hydrate (accuracy is bounded by this; raise for full periods)",
    )
    scan_limit: int = Field(
        default=_SCAN_LIMIT_DEFAULT,
        description="Max candidate mutations pulled before hydration (max 2000)",
    )
    format: str | None = Field(
        default="json", description="'json' (default) or 'markdown'"
    )


class VatSummaryTool(BaseTool):
    """VAT totals per code over a period."""

    name = "get_vat_summary"
    description = (
        "VAT summary over a period: total VAT per VAT code across mutations, with an overall total. "
        "Hydrates mutation detail (bounded by max_details) since the VAT breakdown is detail-only."
    )
    input_schema = VatSummaryInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        scan_limit = min(int(arguments.get("scan_limit", _SCAN_LIMIT_DEFAULT)), 2000)
        max_details = int(arguments.get("max_details", _MAX_DETAILS_DEFAULT))

        candidates = client.mutations.list(
            limit=scan_limit,
            date_filter=range_date_filter(
                arguments.get("date_from"), arguments.get("date_to")
            ),
        ).items
        truncated = len(candidates) > max_details or len(candidates) >= scan_limit
        selected = candidates[:max_details]

        totals: dict[str, float] = defaultdict(float)
        for item in selected:
            detail = client.mutations.get(item.id)
            vat_entries = detail.vat or []
            if vat_entries:
                for entry in vat_entries:
                    code = str(entry.vat_code)
                    totals[code] += float(entry.amount)
            else:
                for row in detail.rows:
                    if row.vat_amount is not None and row.vat_code:
                        totals[str(row.vat_code)] += float(row.vat_amount)

        by_code = [
            {"vat_code": code, "amount": round2(amount)}
            for code, amount in sorted(totals.items())
        ]
        result: dict[str, Any] = {
            "date_from": arguments.get("date_from"),
            "date_to": arguments.get("date_to"),
            "mutations_scanned": len(selected),
            "truncated": truncated,
            "by_code": by_code,
            "total_vat": round2(sum(totals.values())),
        }
        if truncated:
            result["hint"] = (
                "Not all mutations in range were hydrated; raise max_details/scan_limit or narrow the period for exact figures."
            )
        if arguments.get("format") == "markdown":
            result["markdown"] = to_markdown_table(by_code, ["vat_code", "amount"])
        return result


# --------------------------------------------------------------------------- #
# AR/AP aging
# --------------------------------------------------------------------------- #

_BUCKETS = ("0-30", "31-60", "61-90", "90+")


def _bucket_for(age_days: int) -> str:
    if age_days <= 30:
        return "0-30"
    if age_days <= 60:
        return "31-60"
    if age_days <= 90:
        return "61-90"
    return "90+"


def _age_side(
    client: "EBoekhoudenClient", cred_deb: str, reference: datetime.date
) -> dict[str, Any]:
    per_relation: dict[int, dict[str, Any]] = {}
    bucket_totals: dict[str, float] = {bucket: 0.0 for bucket in _BUCKETS}
    grand_total = 0.0

    for invoice in client.mutations.iter_outstanding(cred_deb):
        amount = float(invoice.outstanding_amount)
        age = (reference - invoice.date).days
        bucket = _bucket_for(age)
        bucket_totals[bucket] = round2(bucket_totals[bucket] + amount)
        grand_total += amount

        relation = per_relation.setdefault(
            invoice.relation_id,
            {
                "relation_id": invoice.relation_id,
                "company": invoice.company,
                "total": 0.0,
                "buckets": {b: 0.0 for b in _BUCKETS},
            },
        )
        relation["total"] = round2(relation["total"] + amount)
        relation["buckets"][bucket] = round2(relation["buckets"][bucket] + amount)

    return {
        "total": round2(grand_total),
        "bucket_totals": bucket_totals,
        "relations": list(per_relation.values()),
    }


class ArApAgingInput(ToolSchema):
    cred_deb: str | None = Field(
        default=None,
        description="'D' debtors (AR) or 'C' creditors (AP). Omit for both.",
    )
    reference_date: str | None = Field(
        default=None,
        description="Age invoices relative to this date (YYYY-MM-DD). Defaults to today.",
    )
    format: str | None = Field(
        default="json", description="'json' (default) or 'markdown'"
    )


class ArApAgingTool(BaseTool):
    """Outstanding AR/AP aged into buckets, per relation."""

    name = "get_ar_ap_aging"
    description = (
        "Accounts receivable / payable aging: outstanding invoices bucketed by age "
        "(0-30/31-60/61-90/90+) per relation, with bucket and grand totals. 'D'=debtors, 'C'=creditors."
    )
    input_schema = ArApAgingInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        reference = _pdate(arguments.get("reference_date")) or datetime.date.today()
        requested = arguments.get("cred_deb")
        sides = [requested] if requested else ["D", "C"]

        result: dict[str, Any] = {"reference_date": reference.isoformat()}
        for side in sides:
            key = "debtors" if side == "D" else "creditors"
            result[key] = _age_side(client, side, reference)

        if arguments.get("format") == "markdown":
            markdowns = []
            for side in sides:
                key = "debtors" if side == "D" else "creditors"
                rows = [
                    {
                        "relation_id": r["relation_id"],
                        "company": r["company"],
                        "total": r["total"],
                    }
                    for r in result[key]["relations"]
                ]
                markdowns.append(
                    f"### {key}\n"
                    + to_markdown_table(rows, ["relation_id", "company", "total"])
                )
            result["markdown"] = "\n\n".join(markdowns)
        return result


# --------------------------------------------------------------------------- #
# ledger transactions
# --------------------------------------------------------------------------- #


class LedgerTransactionsInput(ToolSchema):
    ledger_id: int = Field(description="Ledger account id to report transactions for")
    date_from: str | None = Field(
        default=None, description="On/after date (YYYY-MM-DD)"
    )
    date_to: str | None = Field(default=None, description="On/before date (YYYY-MM-DD)")
    max_details: int = Field(
        default=_MAX_DETAILS_DEFAULT, description="Max matching mutations to return"
    )
    scan_limit: int = Field(
        default=_SCAN_LIMIT_DEFAULT,
        description="Max candidate mutations pulled before filtering (max 2000)",
    )
    verbose: bool = Field(
        default=False, description="Return raw JSON instead of compact output"
    )


class LedgerTransactionsTool(BaseTool):
    """All mutations touching a ledger over a period, with a running total."""

    name = "get_ledger_transactions"
    description = (
        "Every mutation that touches a given ledger (on the header or any line) over a period, "
        "with the per-mutation amount attributable to that ledger and a running total."
    )
    input_schema = LedgerTransactionsInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        ledger_id = arguments["ledger_id"]
        verbose = bool(arguments.get("verbose", False))
        scan_limit = min(int(arguments.get("scan_limit", _SCAN_LIMIT_DEFAULT)), 2000)
        max_details = int(arguments.get("max_details", _MAX_DETAILS_DEFAULT))

        candidates = client.mutations.list(
            limit=scan_limit,
            date_filter=range_date_filter(
                arguments.get("date_from"), arguments.get("date_to")
            ),
        ).items
        scan_truncated = len(candidates) >= scan_limit

        rows: list[dict[str, Any]] = []
        total = 0.0
        output_truncated = False
        for item in candidates:
            detail = client.mutations.get(item.id)
            row_amount = sum(
                float(row.amount) for row in detail.rows if row.ledger_id == ledger_id
            )
            header_match = detail.ledger_id == ledger_id
            if row_amount == 0.0 and not header_match:
                continue
            ledger_amount = round2(row_amount if row_amount else float(item.amount))
            total += ledger_amount
            entry = {
                "mutation_id": detail.id,
                "date": item.date,
                "type": detail.type,
                "invoice_number": detail.invoice_number,
                "relation_id": detail.relation_id,
                "ledger_amount": ledger_amount,
            }
            rows.append(entry if verbose else compact(entry))
            if len(rows) >= max_details:
                output_truncated = True
                break

        return {
            "ledger_id": ledger_id,
            "date_from": arguments.get("date_from"),
            "date_to": arguments.get("date_to"),
            "count": len(rows),
            "total": round2(total),
            "truncated": scan_truncated or output_truncated,
            "items": rows,
        }
