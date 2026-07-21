"""Administration models for the e-Boekhouden SDK."""

from __future__ import annotations

from eboekhouden.models.base import EBoekhoudenModel, PaginatedResponse


class AdministrationListItem(EBoekhoudenModel):
    """Administration item in list response."""

    guid: str
    company: str


class AdministrationList(PaginatedResponse[AdministrationListItem]):
    """Paginated list of administrations."""

    pass
