"""Ledger models for the e-Boekhouden SDK."""

from __future__ import annotations

from decimal import Decimal

from pydantic import Field

from eboekhouden.models.base import EBoekhoudenModel, PaginatedResponse
from eboekhouden.models.enums import LedgerCategory


class LedgerListItem(EBoekhoudenModel):
    """Ledger item in list response."""

    id: int
    code: str
    description: str
    category: str


class Ledger(EBoekhoudenModel):
    """Full ledger model."""

    id: int
    code: str
    description: str
    category: str
    group: str | None = None


class LedgerBalance(EBoekhoudenModel):
    """Ledger balance response."""

    code: str
    type: str
    balance: Decimal


class CreateLedger(EBoekhoudenModel):
    """Model for creating a ledger."""

    code: str = Field(max_length=10)
    description: str = Field(max_length=100)
    category: LedgerCategory | None = None
    group: str | None = None


class PatchLedger(EBoekhoudenModel):
    """Model for updating a ledger."""

    code: str | None = Field(default=None, max_length=10)
    description: str | None = Field(default=None, max_length=100)
    category: LedgerCategory | None = None
    group: str | None = Field(default=None, max_length=50)


class LedgerList(PaginatedResponse[LedgerListItem]):
    """Paginated list of ledgers."""

    pass
