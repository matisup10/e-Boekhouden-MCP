"""Batch detail tools: full detail for a list of ids in one MCP call.

Use these when you already hold ids (e.g. from a list_* call or from
list_outstanding_invoices) and want every record's full detail without one
get_* round-trip per id.
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Any, Callable

from pydantic import Field

from eboekhouden_mcp.tools.base import BaseTool, ToolSchema
from eboekhouden_mcp.tools.power._helpers import capped_result, compact, hydrate

if TYPE_CHECKING:
    from eboekhouden import EBoekhoudenClient

_MAX_DETAILS_DEFAULT = 50


def _normalize_ids(raw: Any) -> list[int]:
    """Accept a list, a JSON array string, or a comma/space separated string."""
    if raw in (None, "", []):
        return []
    if isinstance(raw, int):
        return [raw]
    if isinstance(raw, str):
        text = raw.strip()
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = [part for part in re.split(r"[,\s]+", text) if part]
        raw = parsed
    if isinstance(raw, int):
        raw = [raw]
    if not isinstance(raw, list):
        raise ValueError(
            "ids must be an array of integers or a JSON/comma string of integers"
        )
    return [int(value) for value in raw]


def _run_batch(
    getter: Callable[[int], Any],
    arguments: dict[str, Any],
) -> dict[str, Any]:
    ids = _normalize_ids(arguments.get("ids", arguments.get("ids_json")))
    if not ids:
        return {"error": "ids is required and must contain at least one id"}
    verbose = bool(arguments.get("verbose", False))
    cap = int(arguments.get("max_details", _MAX_DETAILS_DEFAULT))

    items, truncated, total = hydrate(getter, ids, cap)
    if not verbose:
        items = [compact(item) for item in items]
    return capped_result(
        items,
        truncated,
        total,
        hint="More ids than max_details; split the batch or raise max_details.",
    )


def _ids_schema(entity: str) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "ids": {
                "type": "array",
                "description": f"{entity} ids to fetch. Use an actual JSON array of integers.",
                "minItems": 1,
                "maxItems": 2000,
                "items": {"type": "integer", "minimum": 1},
            },
            "ids_json": {
                "type": "string",
                "description": "Fallback only: JSON array or comma-separated ids. Prefer ids.",
            },
            "max_details": {
                "type": "integer",
                "minimum": 1,
                "maximum": 2000,
                "description": "Max records to fetch/return (cap guards token cost).",
            },
            "verbose": {
                "type": "boolean",
                "description": "Return raw JSON with all null fields instead of compact output.",
            },
        },
        "additionalProperties": False,
    }


class _BatchInput(ToolSchema):
    ids: list[int] | None = Field(
        default=None,
        min_length=1,
        max_length=2000,
        description="Ids to fetch",
    )
    ids_json: str | None = Field(
        default=None, description="Fallback JSON or comma-separated ids"
    )
    max_details: int = Field(
        default=_MAX_DETAILS_DEFAULT,
        ge=1,
        le=2000,
        description="Max records to fetch/return",
    )
    verbose: bool = Field(
        default=False, description="Return raw JSON instead of compact output"
    )


class GetMutationsBatchTool(BaseTool):
    """Fetch full detail for many mutations at once."""

    name = "get_mutations_batch"
    description = "Fetch full detail (rows, VAT, relation) for a list of mutation ids in one call."
    input_schema = _BatchInput

    def get_schema(self) -> dict[str, Any]:
        return _ids_schema("Mutation")

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        return _run_batch(client.mutations.get, arguments)


class GetRelationsBatchTool(BaseTool):
    """Fetch full detail for many relations at once."""

    name = "get_relations_batch"
    description = "Fetch full detail (name, address, IBAN, etc.) for a list of relation ids in one call."
    input_schema = _BatchInput

    def get_schema(self) -> dict[str, Any]:
        return _ids_schema("Relation")

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        return _run_batch(client.relations.get, arguments)


class GetInvoicesBatchTool(BaseTool):
    """Fetch full detail for many invoices at once."""

    name = "get_invoices_batch"
    description = (
        "Fetch full detail (line items, VAT) for a list of invoice ids in one call."
    )
    input_schema = _BatchInput

    def get_schema(self) -> dict[str, Any]:
        return _ids_schema("Invoice")

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        return _run_batch(client.invoices.get, arguments)
