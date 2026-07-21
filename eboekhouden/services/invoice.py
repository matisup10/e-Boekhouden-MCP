"""Invoice service for the e-Boekhouden SDK."""

from __future__ import annotations

import datetime
from typing import Generator

from eboekhouden.filters import Filter
from eboekhouden.models.invoice import (
    CreateInvoice,
    CreatedInvoice,
    Invoice,
    InvoiceList,
    InvoiceListItem,
)
from eboekhouden.services.base import BaseService


class InvoiceService(BaseService):
    """Service for invoice endpoints."""

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        invoice_number: str | Filter | None = None,
        relation_id: int | None = None,
        date_filter: datetime.date | Filter | None = None,
    ) -> InvoiceList:
        """Get all invoices.

        Args:
            limit: Number of items to retrieve (max 2000)
            offset: Number of items to skip
            invoice_number: Filter by invoice number
            relation_id: Filter by relation ID
            date_filter: Filter by invoice date

        Returns:
            Paginated list of invoices
        """
        params = self._build_params(
            limit=limit,
            offset=offset,
            invoiceNumber=invoice_number,
            relationId=relation_id,
            date=date_filter,
        )
        response = self._get("/v1/invoice", params)
        return InvoiceList.model_validate(response.json())

    def get(self, id: int) -> Invoice:
        """Get an invoice by ID.

        Args:
            id: Invoice ID

        Returns:
            Full invoice details with line items
        """
        response = self._get(f"/v1/invoice/{id}")
        return Invoice.model_validate(response.json())

    def create(self, invoice: CreateInvoice) -> CreatedInvoice:
        """Create a new invoice.

        Args:
            invoice: Invoice data with items

        Returns:
            Created invoice ID and number
        """
        response = self._post("/v1/invoice", self._model_to_dict(invoice))
        return CreatedInvoice.model_validate(response.json())

    def iter_all(
        self, limit: int = 100, **kwargs
    ) -> Generator[InvoiceListItem, None, None]:
        """Iterate through all invoices.

        Args:
            limit: Items per page
            **kwargs: Filter parameters

        Yields:
            Individual invoices
        """
        return self._paginate(
            "/v1/invoice",
            InvoiceList,
            InvoiceListItem,
            limit=limit,
            **kwargs,
        )
