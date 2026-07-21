"""Unit service for the e-Boekhouden SDK."""

from typing import Generator

from eboekhouden.models.unit import Unit, UnitList
from eboekhouden.services.base import BaseService


class UnitService(BaseService):
    """Service for unit endpoints."""

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> UnitList:
        """Get all units.

        Args:
            limit: Number of items to retrieve (max 2000)
            offset: Number of items to skip

        Returns:
            Paginated list of units
        """
        params = self._build_params(limit=limit, offset=offset)
        response = self._get("/v1/unit", params)
        return UnitList.model_validate(response.json())

    def iter_all(self, limit: int = 100) -> Generator[Unit, None, None]:
        """Iterate through all units.

        Args:
            limit: Items per page

        Yields:
            Individual units
        """
        return self._paginate(
            "/v1/unit",
            UnitList,
            Unit,
            limit=limit,
        )
