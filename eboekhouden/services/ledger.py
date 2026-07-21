"""Ledger service for the e-Boekhouden SDK."""

from __future__ import annotations

import datetime
from typing import Generator

from eboekhouden.filters import Filter
from eboekhouden.models.ledger import (
    CreateLedger,
    Ledger,
    LedgerBalance,
    LedgerList,
    LedgerListItem,
    PatchLedger,
)
from eboekhouden.services.base import BaseService


class LedgerService(BaseService):
    """Service for ledger endpoints."""

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        code: str | Filter | None = None,
        category: str | Filter | None = None,
    ) -> LedgerList:
        """Get all ledgers.

        Args:
            limit: Number of items to retrieve (max 2000)
            offset: Number of items to skip
            code: Filter by ledger code
            category: Filter by category

        Returns:
            Paginated list of ledgers
        """
        params = self._build_params(
            limit=limit,
            offset=offset,
            code=code,
            category=category,
        )
        response = self._get("/v1/ledger", params)
        return LedgerList.model_validate(response.json())

    def get(self, id: int) -> Ledger:
        """Get a ledger by ID.

        Args:
            id: Ledger ID

        Returns:
            Full ledger details
        """
        response = self._get(f"/v1/ledger/{id}")
        return Ledger.model_validate(response.json())

    def create(self, ledger: CreateLedger) -> int:
        """Create a new ledger.

        Args:
            ledger: Ledger data

        Returns:
            Created ledger ID
        """
        response = self._post("/v1/ledger", self._model_to_dict(ledger))
        return response.json()["id"]

    def update(self, id: int, ledger: PatchLedger) -> None:
        """Update a ledger.

        Args:
            id: Ledger ID
            ledger: Updated ledger data
        """
        self._patch(f"/v1/ledger/{id}", self._model_to_dict(ledger))

    def get_balance(
        self,
        id: int,
        *,
        cost_center_id: int | None = None,
        from_date: datetime.date | None = None,
        to_date: datetime.date | None = None,
    ) -> LedgerBalance:
        """Get the balance of a ledger.

        Args:
            id: Ledger ID
            cost_center_id: Filter by cost center
            from_date: Start date for period balance
            to_date: End date for balance

        Returns:
            Ledger balance information
        """
        params = {}
        if cost_center_id is not None:
            params["costCenterId"] = str(cost_center_id)
        if from_date is not None:
            params["from"] = from_date.isoformat()
        if to_date is not None:
            params["to"] = to_date.isoformat()

        response = self._get(f"/v1/ledger/{id}/balance", params or None)
        return LedgerBalance.model_validate(response.json())

    def iter_all(
        self, limit: int = 100, **kwargs
    ) -> Generator[LedgerListItem, None, None]:
        """Iterate through all ledgers.

        Args:
            limit: Items per page
            **kwargs: Filter parameters

        Yields:
            Individual ledgers
        """
        return self._paginate(
            "/v1/ledger",
            LedgerList,
            LedgerListItem,
            limit=limit,
            **kwargs,
        )
