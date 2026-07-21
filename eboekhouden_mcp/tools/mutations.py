"""Mutation tools for the e-Boekhouden MCP server."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Literal

from pydantic import Field, field_validator

from eboekhouden.models.mutation import CreateMutation, CreateMutationRow
from eboekhouden_mcp.tools.base import BaseTool, PaginatedInput, ToolSchema

if TYPE_CHECKING:
    from eboekhouden import EBoekhoudenClient


class ListMutationsInput(PaginatedInput):
    """Input schema for list_mutations tool."""

    type: int | None = Field(
        default=None,
        description="Mutation type (1-7): 1=Invoice received, 2=Invoice sent, 3=Payment received, 4=Payment made, 5=Bank/cash, 6=Deposit, 7=General journal",
    )
    description: str | None = Field(default=None, description="Filter by description")
    invoice_number: str | None = Field(
        default=None, description="Filter by invoice number"
    )
    date: str | None = Field(default=None, description="Filter by date (YYYY-MM-DD)")


class ListMutationsTool(BaseTool):
    """List all mutations (journal entries)."""

    name = "list_mutations"
    description = "List all mutations (journal entries) with optional filters for type, description, invoice number, and date"
    input_schema = ListMutationsInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        result = client.mutations.list(
            limit=arguments.get("limit"),
            offset=arguments.get("offset"),
            type=arguments.get("type"),
            description=arguments.get("description"),
            invoice_number=arguments.get("invoice_number"),
            date_filter=arguments.get("date"),
        )
        return {
            "count": result.count,
            "items": [item.model_dump() for item in result.items],
        }


class GetMutationInput(ToolSchema):
    """Input schema for get_mutation tool."""

    id: int = Field(description="Mutation ID")


class GetMutationTool(BaseTool):
    """Get a mutation by ID."""

    name = "get_mutation"
    description = "Get full details of a mutation (journal entry) by ID, including all debit/credit rows"
    input_schema = GetMutationInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        mutation = client.mutations.get(arguments["id"])
        return mutation.model_dump()


class MutationRowInput(ToolSchema):
    """Input schema for a mutation row."""

    vat_code: str
    amount: float
    ledger_id: int | None = Field(default=None, ge=1)
    vat_amount: float | None = None
    cost_center_id: int | None = Field(default=None, ge=1)
    description: str | None = None
    invoice_number: str | None = None
    relation_id: int | None = Field(default=None, ge=1)


class CreateMutationInput(ToolSchema):
    """Input schema for create_mutation tool."""

    type: Literal["1", "2", "3", "4", "5", "6", "7"] = Field(
        description="Mutation type as string: 1=Invoice received, 2=Invoice sent, 3=Payment received, 4=Payment made, 5=Money received, 6=Money sent, 7=General journal"
    )
    date: str = Field(description="Mutation date (YYYY-MM-DD)")
    ledger_id: int = Field(description="Main ledger account ID for the mutation")
    rows: list[MutationRowInput] | MutationRowInput | str | None = Field(
        default=None,
        description="Mutation rows as an array of objects. Also accepts a JSON string containing one row object or an array of row objects.",
    )
    rows_json: str | None = Field(
        default=None,
        description="Fallback JSON string containing mutation rows",
    )
    description: str | None = Field(
        default=None, description="Description (max 50 chars)"
    )
    invoice_number: str | None = Field(
        default=None, description="Invoice number for reference (max 50 chars)"
    )
    relation_id: int | str | None = Field(default=None, description="Relation ID")
    term_of_payment: int | None = Field(
        default=None, description="Payment term in days"
    )
    in_ex_vat: str | None = Field(
        default=None, description="'IN' for VAT inclusive, 'EX' for VAT exclusive"
    )

    @field_validator("type", mode="before")
    @classmethod
    def _coerce_type(cls, value: Any) -> str:
        return str(value) if isinstance(value, int) else value


class CreateMutationTool(BaseTool):
    """Create a new mutation (journal entry)."""

    name = "create_mutation"
    description = "Create a new mutation (journal entry). Requires type, date, and ledger_id. Optional rows for detailed line items with vat_code and amount."
    input_schema = CreateMutationInput

    def get_schema(self) -> dict[str, Any]:
        """Return a Claude Desktop-friendly schema without anyOf unions."""
        return {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["1", "2", "3", "4", "5", "6", "7"],
                    "description": "Mutation type as string: 1=Invoice received, 2=Invoice sent, 3=Payment received, 4=Payment made, 5=Money received, 6=Money sent, 7=General journal",
                },
                "date": {
                    "type": "string",
                    "format": "date",
                    "description": "Mutation date (YYYY-MM-DD)",
                },
                "ledger_id": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Main ledger account ID for the mutation",
                },
                "rows": {
                    "type": "array",
                    "maxItems": 500,
                    "description": "Mutation rows. Use an actual JSON array, not a string.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "ledger_id": {
                                "type": "integer",
                                "minimum": 1,
                                "description": "Ledger account ID for this row",
                            },
                            "vat_code": {
                                "type": "string",
                                "description": "VAT code, e.g. BU_EU_INK or GEEN",
                            },
                            "amount": {"type": "number", "description": "Row amount"},
                            "vat_amount": {
                                "type": "number",
                                "description": "VAT amount for divergent VAT codes",
                            },
                            "cost_center_id": {
                                "type": "integer",
                                "minimum": 1,
                                "description": "Cost center ID",
                            },
                            "description": {
                                "type": "string",
                                "description": "Row description",
                            },
                            "invoice_number": {
                                "type": "string",
                                "description": "Invoice number for payment rows",
                            },
                            "relation_id": {
                                "type": "integer",
                                "minimum": 1,
                                "description": "Relation ID for payment rows",
                            },
                        },
                        "required": ["vat_code", "amount"],
                        "additionalProperties": False,
                    },
                },
                "rows_json": {
                    "type": "string",
                    "description": "Fallback only: JSON string containing one row object or an array of row objects. Prefer rows.",
                },
                "description": {
                    "type": "string",
                    "maxLength": 50,
                    "description": "Description (max 50 chars)",
                },
                "invoice_number": {
                    "type": "string",
                    "maxLength": 50,
                    "description": "Invoice number for reference (max 50 chars)",
                },
                "relation_id": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Relation ID",
                },
                "term_of_payment": {
                    "type": "integer",
                    "description": "Payment term in days",
                },
                "in_ex_vat": {
                    "type": "string",
                    "enum": ["IN", "EX"],
                    "description": "'IN' for VAT inclusive, 'EX' for VAT exclusive",
                },
            },
            "required": ["type", "date", "ledger_id"],
            "additionalProperties": False,
        }

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        # Convert row dicts to CreateMutationRow models if provided
        rows = None
        normalized_rows = _normalize_mutation_rows(
            arguments.get("rows", arguments.get("rows_json"))
        )
        if normalized_rows:
            rows = []
            for row_data in normalized_rows:
                rows.append(
                    CreateMutationRow(
                        vat_code=row_data["vat_code"],
                        amount=row_data["amount"],
                        ledger_id=row_data.get("ledger_id"),
                        vat_amount=row_data.get("vat_amount"),
                        cost_center_id=row_data.get("cost_center_id"),
                        description=row_data.get("description"),
                        invoice_number=row_data.get("invoice_number"),
                        relation_id=row_data.get("relation_id"),
                    )
                )

        mutation_data = CreateMutation(
            type=str(arguments["type"]),
            date=arguments["date"],
            ledger_id=arguments["ledger_id"],
            rows=rows,
            description=arguments.get("description"),
            invoice_number=arguments.get("invoice_number"),
            relation_id=arguments.get("relation_id"),
            term_of_payment=arguments.get("term_of_payment"),
            in_ex_vat=arguments.get("in_ex_vat"),
        )
        result = client.mutations.create(mutation_data)
        return {"id": result.id}


def _normalize_mutation_rows(rows: Any) -> list[dict[str, Any]] | None:
    """Accept structured rows or JSON-stringified rows from MCP clients."""
    if rows in (None, "", []):
        return None

    if isinstance(rows, str):
        try:
            rows = json.loads(rows)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "rows must be an array/object or a JSON string containing row data"
            ) from exc

    if isinstance(rows, dict):
        rows = [rows]

    if not isinstance(rows, list):
        raise ValueError("rows must be an array of row objects")

    normalized: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("each mutation row must be an object")
        normalized.append(row)
    return normalized


class ListOutstandingInvoicesInput(PaginatedInput):
    """Input schema for list_outstanding_invoices tool."""

    cred_deb: str = Field(
        description="'C' for creditors (bills to pay) or 'D' for debtors (invoices to receive)"
    )
    invoice_number: str | None = Field(
        default=None, description="Filter by invoice number"
    )


class ListOutstandingInvoicesTool(BaseTool):
    """List outstanding invoices."""

    name = "list_outstanding_invoices"
    description = "List outstanding (unpaid) invoices. Use 'D' for debtors (amounts to receive) or 'C' for creditors (amounts to pay)"
    input_schema = ListOutstandingInvoicesInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        result = client.mutations.list_outstanding(
            cred_deb=arguments["cred_deb"],
            limit=arguments.get("limit"),
            offset=arguments.get("offset"),
            invoice_number=arguments.get("invoice_number"),
        )
        return {
            "count": result.count,
            "items": [item.model_dump() for item in result.items],
        }
