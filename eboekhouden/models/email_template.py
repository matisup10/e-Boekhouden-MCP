"""Email template models for the e-Boekhouden SDK."""

from __future__ import annotations

from pydantic import Field

from eboekhouden.models.base import EBoekhoudenModel, PaginatedResponse


class EmailTemplateListItem(EBoekhoudenModel):
    """Email template item in list response."""

    id: int
    name: str
    use_invoice: bool = Field(alias="useInvoice")
    use_quote: bool = Field(alias="useQuote")
    use_mailing: bool = Field(alias="useMailing")


class EmailTemplateList(PaginatedResponse[EmailTemplateListItem]):
    """Paginated list of email templates."""

    pass
