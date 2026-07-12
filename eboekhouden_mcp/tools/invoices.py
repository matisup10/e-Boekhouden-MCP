"""Invoice tools for the e-Boekhouden MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import Field

from eboekhouden.models.invoice import CreateInvoice, CreateInvoiceItem
from eboekhouden_mcp.tools.base import BaseTool, ToolSchema

if TYPE_CHECKING:
    from eboekhouden import EBoekhoudenClient


class ListInvoicesInput(ToolSchema):
    """Input schema for list_invoices tool."""

    limit: int | None = Field(default=None, description="Number of items to retrieve (max 2000)")
    offset: int | None = Field(default=None, description="Number of items to skip")
    invoice_number: str | None = Field(default=None, description="Filter by invoice number")
    relation_id: int | None = Field(default=None, description="Filter by relation ID")
    date: str | None = Field(default=None, description="Filter by invoice date (YYYY-MM-DD)")


class ListInvoicesTool(BaseTool):
    """List all invoices."""

    name = "list_invoices"
    description = "List all invoices with optional filters for invoice number, relation, and date"
    input_schema = ListInvoicesInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        result = client.invoices.list(
            limit=arguments.get("limit"),
            offset=arguments.get("offset"),
            invoice_number=arguments.get("invoice_number"),
            relation_id=arguments.get("relation_id"),
            date_filter=arguments.get("date"),
        )
        return {
            "count": result.count,
            "items": [item.model_dump() for item in result.items],
        }


class GetInvoiceInput(ToolSchema):
    """Input schema for get_invoice tool."""

    id: int = Field(description="Invoice ID")


class GetInvoiceTool(BaseTool):
    """Get an invoice by ID."""

    name = "get_invoice"
    description = "Get full details of an invoice by ID, including all line items, totals, VAT amounts, and PDF URL"
    input_schema = GetInvoiceInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        invoice = client.invoices.get(arguments["id"])
        return invoice.model_dump()


class InvoiceItemInput(ToolSchema):
    """Input schema for an invoice line item."""

    description: str = Field(description="Line item description")
    vat_code: str = Field(description="VAT code (e.g., 'HOOG_VERK_21' for 21% Dutch VAT)")
    ledger_id: int = Field(description="Ledger account ID")
    quantity: float | None = Field(default=None, description="Quantity")
    price_per_unit: float | None = Field(default=None, description="Price per unit")
    cost_center_id: int | None = Field(default=None, description="Cost center ID")


class CreateInvoiceInput(ToolSchema):
    """Input schema for create_invoice tool."""

    relation_id: int = Field(description="Relation (customer) ID")
    term_of_payment: int = Field(description="Payment term in days")
    template_id: int = Field(description="Invoice template ID")
    items: list[dict] = Field(description="List of invoice line items")
    invoice_number: str | None = Field(default=None, description="Custom invoice number (auto-generated if not provided)")
    date: str | None = Field(default=None, description="Invoice date (YYYY-MM-DD, defaults to today)")
    in_ex_vat: str | None = Field(default=None, description="'IN' for VAT inclusive, 'EX' for VAT exclusive")
    reference: str | None = Field(default=None, description="Reference text (max 50 chars)")
    text: str | None = Field(default=None, description="Invoice text/notes (max 35000 chars)")


class CreateInvoiceTool(BaseTool):
    """Create a new invoice."""

    name = "create_invoice"
    description = "Create a new invoice for a customer with line items. Each item needs description, VAT code, ledger ID, quantity, and price."
    input_schema = CreateInvoiceInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        # Convert item dicts to CreateInvoiceItem models
        items = []
        for item_data in arguments["items"]:
            items.append(
                CreateInvoiceItem(
                    description=item_data["description"],
                    vat_code=item_data["vat_code"],
                    ledger_id=item_data["ledger_id"],
                    quantity=item_data.get("quantity"),
                    price_per_unit=item_data.get("price_per_unit"),
                    cost_center_id=item_data.get("cost_center_id"),
                )
            )

        invoice_data = CreateInvoice(
            relation_id=arguments["relation_id"],
            term_of_payment=arguments["term_of_payment"],
            template_id=arguments["template_id"],
            items=items,
            invoice_number=arguments.get("invoice_number"),
            date=arguments.get("date"),
            in_ex_vat=arguments.get("in_ex_vat"),
            reference=arguments.get("reference"),
            text=arguments.get("text"),
        )
        result = client.invoices.create(invoice_data)
        return {
            "id": result.id,
            "invoice_number": result.invoice_number,
            "in_ex_vat": result.in_ex_vat,
        }
