"""Email template service for the e-Boekhouden SDK."""

from typing import Generator

from eboekhouden.models.email_template import EmailTemplateList, EmailTemplateListItem
from eboekhouden.services.base import BaseService


class EmailTemplateService(BaseService):
    """Service for email template endpoints."""

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> EmailTemplateList:
        """Get all email templates.

        Args:
            limit: Number of items to retrieve (max 2000)
            offset: Number of items to skip

        Returns:
            Paginated list of email templates
        """
        params = self._build_params(limit=limit, offset=offset)
        response = self._get("/v1/emailtemplate", params)
        return EmailTemplateList.model_validate(response.json())

    def iter_all(
        self, limit: int = 100
    ) -> Generator[EmailTemplateListItem, None, None]:
        """Iterate through all email templates.

        Args:
            limit: Items per page

        Yields:
            Individual email templates
        """
        return self._paginate(
            "/v1/emailtemplate",
            EmailTemplateList,
            EmailTemplateListItem,
            limit=limit,
        )
