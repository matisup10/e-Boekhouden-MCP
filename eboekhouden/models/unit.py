"""Unit models for the e-Boekhouden SDK."""

from __future__ import annotations

from eboekhouden.models.base import EBoekhoudenModel, PaginatedResponse


class Unit(EBoekhoudenModel):
    """Unit model."""

    id: int
    description: str


class UnitList(PaginatedResponse[Unit]):
    """Paginated list of units."""

    pass
