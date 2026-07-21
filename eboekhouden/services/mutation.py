"""Mutation service for the e-Boekhouden SDK."""

from __future__ import annotations

import datetime
from typing import Generator

from eboekhouden.filters import Filter
from eboekhouden.models.mutation import (
    CreateMutation,
    CreatedMutation,
    Mutation,
    MutationList,
    MutationListItem,
    OutstandingInvoice,
    OutstandingInvoicesList,
)
from eboekhouden.services.base import BaseService


class MutationService(BaseService):
    """Service for mutation endpoints."""

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        type: int | None = None,
        id_filter: int | Filter | None = None,
        description: str | Filter | None = None,
        invoice_number: str | Filter | None = None,
        date_filter: datetime.date | Filter | None = None,
    ) -> MutationList:
        """Get all mutations.

        Args:
            limit: Number of items to retrieve (max 2000)
            offset: Number of items to skip
            type: Filter by mutation type (1-7)
            id_filter: Filter by mutation ID
            description: Filter by description
            invoice_number: Filter by invoice number
            date_filter: Filter by date

        Returns:
            Paginated list of mutations
        """
        params = self._build_params(
            limit=limit,
            offset=offset,
            type=type,
            id=id_filter,
            description=description,
            invoiceNumber=invoice_number,
            date=date_filter,
        )
        response = self._get("/v1/mutation", params)
        return MutationList.model_validate(response.json())

    def get(self, id: int) -> Mutation:
        """Get a mutation by ID.

        Args:
            id: Mutation ID

        Returns:
            Full mutation details with rows
        """
        response = self._get(f"/v1/mutation/{id}")
        return Mutation.model_validate(response.json())

    def create(self, mutation: CreateMutation) -> CreatedMutation:
        """Create a new mutation.

        Args:
            mutation: Mutation data with rows

        Returns:
            Created mutation ID
        """
        response = self._post("/v1/mutation", self._model_to_dict(mutation))
        return CreatedMutation.model_validate(response.json())

    def list_outstanding(
        self,
        cred_deb: str,
        *,
        limit: int | None = None,
        offset: int | None = None,
        invoice_number: str | Filter | None = None,
    ) -> OutstandingInvoicesList:
        """Get all outstanding invoices.

        Args:
            cred_deb: 'C' for creditors or 'D' for debtors
            limit: Number of items to retrieve (max 2000)
            offset: Number of items to skip
            invoice_number: Filter by invoice number

        Returns:
            Paginated list of outstanding invoices
        """
        params = self._build_params(
            limit=limit,
            offset=offset,
            credDeb=cred_deb,
            invoiceNumber=invoice_number,
        )
        response = self._get("/v1/mutation/invoice/outstanding", params)
        return OutstandingInvoicesList.model_validate(response.json())

    def iter_all(
        self, limit: int = 100, **kwargs
    ) -> Generator[MutationListItem, None, None]:
        """Iterate through all mutations.

        Args:
            limit: Items per page
            **kwargs: Filter parameters

        Yields:
            Individual mutations
        """
        return self._paginate(
            "/v1/mutation",
            MutationList,
            MutationListItem,
            limit=limit,
            **kwargs,
        )

    def iter_outstanding(
        self,
        cred_deb: str,
        limit: int = 100,
        **kwargs,
    ) -> Generator[OutstandingInvoice, None, None]:
        """Iterate through all outstanding invoices.

        Args:
            cred_deb: 'C' for creditors or 'D' for debtors
            limit: Items per page
            **kwargs: Filter parameters

        Yields:
            Individual outstanding invoices
        """
        return self._paginate(
            "/v1/mutation/invoice/outstanding",
            OutstandingInvoicesList,
            OutstandingInvoice,
            limit=limit,
            credDeb=cred_deb,
            **kwargs,
        )
