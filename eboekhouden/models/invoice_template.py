"""Invoice template models for the e-Boekhouden SDK."""

from __future__ import annotations

from eboekhouden.models.base import EBoekhoudenModel, PaginatedResponse


class InvoiceTemplateListItem(EBoekhoudenModel):
    """Invoice template item in list response."""

    id: int
    name: str
    active: bool
    type: str  # 'E' = Editor, 'A' = Advanced


class InvoiceTemplateList(PaginatedResponse[InvoiceTemplateListItem]):
    """Paginated list of invoice templates."""

    pass
