"""Enriched search tools: multi-field filters, auto-hydration, compact output.

These sit on top of the SDK list/get methods. They exist to collapse the common
"list, then get() each id" pattern into a single MCP call, and to filter on
fields the API cannot filter server-side (relation/ledger/cost-center/amount).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import Field

from eboekhouden.filters import StringFilter
from eboekhouden_mcp.tools.base import BaseTool, ToolSchema
from eboekhouden_mcp.tools.power._helpers import (
    apply_filters,
    capped_result,
    compact,
    range_date_filter,
    range_int_filter,
)

if TYPE_CHECKING:
    from eboekhouden import EBoekhoudenClient

_SCAN_LIMIT_DEFAULT = 500
_MAX_DETAILS_DEFAULT = 50


def _like(value: str | None) -> StringFilter | None:
    return StringFilter.contains(value) if value else None


def _dump(obj: Any, verbose: bool) -> dict[str, Any]:
    data = obj.model_dump() if hasattr(obj, "model_dump") else obj
    return data if verbose else compact(data)


# --------------------------------------------------------------------------- #
# search_relations
# --------------------------------------------------------------------------- #


class SearchRelationsInput(ToolSchema):
    """Input schema for search_relations."""

    name: str | None = Field(default=None, description="Match company/person name (contains)")
    email: str | None = Field(default=None, description="Match email address (contains)")
    city: str | None = Field(default=None, description="Match city (contains)")
    code: str | None = Field(default=None, description="Match relation code (contains)")
    contact: str | None = Field(default=None, description="Match contact name (contains)")
    type: str | None = Field(default=None, description="Relation type: 'B' business or 'P' private")
    hydrate: bool = Field(default=True, description="Fetch full detail per match (name, address, IBAN, etc.). The list endpoint only returns id/type/code.")
    max_details: int = Field(default=_MAX_DETAILS_DEFAULT, description="Max records to hydrate/return (cap guards token cost)")
    scan_limit: int = Field(default=_SCAN_LIMIT_DEFAULT, description="Max candidates pulled from the API before hydration (max 2000)")
    verbose: bool = Field(default=False, description="Return raw JSON with all null fields instead of compact output")


class SearchRelationsTool(BaseTool):
    """Search relations and return full detail in one call."""

    name = "search_relations"
    description = (
        "Search relations (customers/suppliers) by name/email/city/code/contact/type and return "
        "FULL details in one call. Replaces list_relations + one get_relation per match — the "
        "relation list endpoint only returns id/type/code, so this is the way to find a relation by name."
    )
    input_schema = SearchRelationsInput

    async def execute(self, client: "EBoekhoudenClient", arguments: dict[str, Any]) -> dict[str, Any]:
        verbose = bool(arguments.get("verbose", False))
        max_details = int(arguments.get("max_details", _MAX_DETAILS_DEFAULT))
        scan_limit = min(int(arguments.get("scan_limit", _SCAN_LIMIT_DEFAULT)), 2000)

        candidates = client.relations.list(
            limit=scan_limit,
            name=_like(arguments.get("name")),
            email=_like(arguments.get("email")),
            city=_like(arguments.get("city")),
            code=_like(arguments.get("code")),
            contact=_like(arguments.get("contact")),
            type=arguments.get("type"),
        ).items

        total = len(candidates)
        if not arguments.get("hydrate", True):
            items = [_dump(c, verbose) for c in candidates[:max_details]]
            truncated = total > max_details
            return capped_result(items, truncated, total, hint="Raise max_details or narrow filters.")

        selected = candidates[:max_details]
        items = [_dump(client.relations.get(c.id), verbose) for c in selected]
        truncated = total > max_details
        return capped_result(
            items,
            truncated,
            total,
            hint="More matches than max_details; narrow name/city or raise max_details.",
        )


# --------------------------------------------------------------------------- #
# search_mutations
# --------------------------------------------------------------------------- #


class SearchMutationsInput(ToolSchema):
    """Input schema for search_mutations."""

    type: int | None = Field(default=None, description="Mutation type 1-7 (exact)")
    date_from: str | None = Field(default=None, description="On/after date (YYYY-MM-DD)")
    date_to: str | None = Field(default=None, description="On/before date (YYYY-MM-DD)")
    id_from: int | None = Field(default=None, description="Minimum mutation id")
    id_to: int | None = Field(default=None, description="Maximum mutation id")
    description: str | None = Field(default=None, description="Match description (contains)")
    invoice_number: str | None = Field(default=None, description="Match invoice number (contains)")
    relation_id: int | None = Field(default=None, description="Only mutations involving this relation (needs detail; forces hydrate)")
    ledger_id: int | None = Field(default=None, description="Only mutations touching this ledger on the header or any line")
    cost_center_id: int | None = Field(default=None, description="Only mutations with a line on this cost center (needs detail; forces hydrate)")
    amount_min: float | None = Field(default=None, description="Minimum mutation amount")
    amount_max: float | None = Field(default=None, description="Maximum mutation amount")
    hydrate: bool = Field(default=True, description="Include line rows, VAT breakdown, relation and description (list omits these)")
    max_details: int = Field(default=_MAX_DETAILS_DEFAULT, description="Max detailed mutations to return")
    scan_limit: int = Field(default=_SCAN_LIMIT_DEFAULT, description="Max candidates pulled from the API before filtering (max 2000)")
    verbose: bool = Field(default=False, description="Return raw JSON instead of compact output")


class SearchMutationsTool(BaseTool):
    """Search mutations across many fields with auto-hydrated line detail."""

    name = "search_mutations"
    description = (
        "Search mutations (journal entries) with server-side type/date/id/description/invoice filters "
        "PLUS client-side relation/ledger/cost-center/amount filters, returning full line-level detail "
        "(rows, VAT, relation) in one call. Replaces list_mutations + one get_mutation per row."
    )
    input_schema = SearchMutationsInput

    async def execute(self, client: "EBoekhoudenClient", arguments: dict[str, Any]) -> dict[str, Any]:
        verbose = bool(arguments.get("verbose", False))
        max_details = int(arguments.get("max_details", _MAX_DETAILS_DEFAULT))
        scan_limit = min(int(arguments.get("scan_limit", _SCAN_LIMIT_DEFAULT)), 2000)

        relation_id = arguments.get("relation_id")
        ledger_id = arguments.get("ledger_id")
        cost_center_id = arguments.get("cost_center_id")
        amount_min = arguments.get("amount_min")
        amount_max = arguments.get("amount_max")

        candidates = client.mutations.list(
            limit=scan_limit,
            type=arguments.get("type"),
            id_filter=range_int_filter(arguments.get("id_from"), arguments.get("id_to")),
            description=_like(arguments.get("description")),
            invoice_number=_like(arguments.get("invoice_number")),
            date_filter=range_date_filter(arguments.get("date_from"), arguments.get("date_to")),
        ).items
        scan_truncated = len(candidates) >= scan_limit

        # Amount lives on the list item only (the detail model has no top-level amount),
        # so it is always a cheap list-level prefilter.
        candidates = apply_filters(
            candidates,
            {
                "amount_min": lambda m: amount_min is None or float(m.amount) >= amount_min,
                "amount_max": lambda m: amount_max is None or float(m.amount) <= amount_max,
            },
        )

        detail_only = relation_id is not None or cost_center_id is not None
        needs_detail = bool(arguments.get("hydrate", True)) or detail_only

        if not needs_detail:
            if ledger_id is not None:
                candidates = [m for m in candidates if m.ledger_id == ledger_id]
            items = [_dump(m, verbose) for m in candidates[:max_details]]
            truncated = scan_truncated or len(candidates) > max_details
            return capped_result(
                items, truncated, len(candidates),
                hint="Narrow date range or raise scan_limit/max_details.",
            )

        out: list[dict[str, Any]] = []
        scanned = 0
        output_truncated = False
        for mutation_item in candidates:
            detail = client.mutations.get(mutation_item.id)
            scanned += 1
            if _detail_matches(detail, relation_id, ledger_id, cost_center_id):
                out.append(_dump(detail, verbose))
                if len(out) >= max_details:
                    output_truncated = scanned < len(candidates)
                    break

        truncated = scan_truncated or output_truncated
        return capped_result(
            out, truncated, len(out),
            hint="Reached max_details before scanning all candidates; narrow filters or raise max_details/scan_limit.",
            extra={"scanned": scanned},
        )


def _detail_matches(detail: Any, relation_id: int | None, ledger_id: int | None, cost_center_id: int | None) -> bool:
    if relation_id is not None:
        header = detail.relation_id == relation_id
        rows = any(row.relation_id == relation_id for row in detail.rows)
        if not (header or rows):
            return False
    if ledger_id is not None:
        header = detail.ledger_id == ledger_id
        rows = any(row.ledger_id == ledger_id for row in detail.rows)
        if not (header or rows):
            return False
    if cost_center_id is not None:
        if not any(row.cost_center_id == cost_center_id for row in detail.rows):
            return False
    return True


# --------------------------------------------------------------------------- #
# search_invoices
# --------------------------------------------------------------------------- #


class SearchInvoicesInput(ToolSchema):
    """Input schema for search_invoices."""

    invoice_number: str | None = Field(default=None, description="Match invoice number (contains)")
    relation_id: int | None = Field(default=None, description="Filter by relation id (exact)")
    date_from: str | None = Field(default=None, description="On/after date (YYYY-MM-DD)")
    date_to: str | None = Field(default=None, description="On/before date (YYYY-MM-DD)")
    amount_min: float | None = Field(default=None, description="Minimum invoice total (incl. VAT)")
    amount_max: float | None = Field(default=None, description="Maximum invoice total (incl. VAT)")
    hydrate: bool = Field(default=False, description="Fetch line items per invoice (the list already carries header totals, so this defaults off)")
    max_details: int = Field(default=_MAX_DETAILS_DEFAULT, description="Max invoices to return")
    scan_limit: int = Field(default=_SCAN_LIMIT_DEFAULT, description="Max candidates pulled from the API before filtering (max 2000)")
    verbose: bool = Field(default=False, description="Return raw JSON instead of compact output")


class SearchInvoicesTool(BaseTool):
    """Search invoices with header + optional line-item hydration."""

    name = "search_invoices"
    description = (
        "Search invoices by number/relation/date/amount. Returns header totals by default; set "
        "hydrate=true to also pull line items. Amount filters run client-side on the invoice total."
    )
    input_schema = SearchInvoicesInput

    async def execute(self, client: "EBoekhoudenClient", arguments: dict[str, Any]) -> dict[str, Any]:
        verbose = bool(arguments.get("verbose", False))
        max_details = int(arguments.get("max_details", _MAX_DETAILS_DEFAULT))
        scan_limit = min(int(arguments.get("scan_limit", _SCAN_LIMIT_DEFAULT)), 2000)
        amount_min = arguments.get("amount_min")
        amount_max = arguments.get("amount_max")

        candidates = client.invoices.list(
            limit=scan_limit,
            invoice_number=_like(arguments.get("invoice_number")),
            relation_id=arguments.get("relation_id"),
            date_filter=range_date_filter(arguments.get("date_from"), arguments.get("date_to")),
        ).items
        scan_truncated = len(candidates) >= scan_limit

        candidates = apply_filters(
            candidates,
            {
                "amount_min": lambda inv: amount_min is None or float(inv.total_amount) >= amount_min,
                "amount_max": lambda inv: amount_max is None or float(inv.total_amount) <= amount_max,
            },
        )
        total = len(candidates)
        selected = candidates[:max_details]

        if arguments.get("hydrate", False):
            items = [_dump(client.invoices.get(inv.id), verbose) for inv in selected]
        else:
            items = [_dump(inv, verbose) for inv in selected]

        truncated = scan_truncated or total > max_details
        return capped_result(items, truncated, total, hint="Narrow filters or raise max_details/scan_limit.")
