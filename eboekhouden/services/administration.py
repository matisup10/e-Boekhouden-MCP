"""Administration service for the e-Boekhouden SDK."""

from collections.abc import Generator

from eboekhouden.models.administration import AdministrationList, AdministrationListItem
from eboekhouden.services.base import BaseService


class AdministrationService(BaseService):
    """Service for administration endpoints."""

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> AdministrationList:
        """Get all administrations managed by the authorized accountant.

        Args:
            limit: Number of items to retrieve (max 2000)
            offset: Number of items to skip

        Returns:
            Paginated list of administrations
        """
        params = self._build_params(limit=limit, offset=offset)
        response = self._get("/v1/administration", params)
        return AdministrationList.model_validate(response.json())

    def list_linked(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> AdministrationList:
        """Get all administrations linked to the authorized administration.

        Args:
            limit: Number of items to retrieve (max 2000)
            offset: Number of items to skip

        Returns:
            Paginated list of linked administrations
        """
        params = self._build_params(limit=limit, offset=offset)
        response = self._get("/v1/administration/linked", params)
        return AdministrationList.model_validate(response.json())

    def iter_all(
        self, limit: int = 100
    ) -> Generator[AdministrationListItem, None, None]:
        """Iterate through all administrations.

        Args:
            limit: Items per page

        Returns:
            Iterator yielding administrations
        """
        return self._paginate(
            "/v1/administration",
            AdministrationList,
            AdministrationListItem,
            limit=limit,
        )
