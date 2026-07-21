"""Invoice template service for the e-Boekhouden SDK."""

from typing import Generator

from eboekhouden.filters import Filter
from eboekhouden.models.invoice_template import (
    InvoiceTemplateList,
    InvoiceTemplateListItem,
)
from eboekhouden.services.base import BaseService


class InvoiceTemplateService(BaseService):
    """Service for invoice template endpoints."""

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        name: str | Filter | None = None,
        type: str | None = None,  # 'E' or 'A'
        active: bool | None = None,
    ) -> InvoiceTemplateList:
        """Get all invoice templates.

        Args:
            limit: Number of items to retrieve (max 2000)
            offset: Number of items to skip
            name: Filter by name
            type: Filter by type ('E' = Editor, 'A' = Advanced)
            active: Filter by active status

        Returns:
            Paginated list of invoice templates
        """
        params = self._build_params(
            limit=limit,
            offset=offset,
            name=name,
            type=type,
            active=active,
        )
        response = self._get("/v1/invoicetemplate", params)
        return InvoiceTemplateList.model_validate(response.json())

    def iter_all(
        self, limit: int = 100, **kwargs
    ) -> Generator[InvoiceTemplateListItem, None, None]:
        """Iterate through all invoice templates.

        Args:
            limit: Items per page
            **kwargs: Filter parameters

        Yields:
            Individual invoice templates
        """
        return self._paginate(
            "/v1/invoicetemplate",
            InvoiceTemplateList,
            InvoiceTemplateListItem,
            limit=limit,
            **kwargs,
        )
