"""Cost center service for the e-Boekhouden SDK."""

from typing import Generator

from eboekhouden.filters import Filter
from eboekhouden.models.cost_center import (
    CostCenter,
    CostCenterCreateResponse,
    CostCenterList,
    CostCenterResponse,
    CreateCostCenter,
)
from eboekhouden.services.base import BaseService


class CostCenterService(BaseService):
    """Service for cost center endpoints."""

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        parent_id: str | Filter | None = None,
        description: str | Filter | None = None,
    ) -> CostCenterList:
        """Get all cost centers.

        Args:
            limit: Number of items to retrieve (max 2000)
            offset: Number of items to skip
            parent_id: Filter by parent ID
            description: Filter by description

        Returns:
            Paginated list of cost centers
        """
        params = self._build_params(
            limit=limit,
            offset=offset,
            parentId=parent_id,
            description=description,
        )
        response = self._get("/v1/costcenter", params)
        return CostCenterList.model_validate(response.json())

    def get(self, id: int) -> CostCenterResponse:
        """Get a cost center by ID.

        Args:
            id: Cost center ID

        Returns:
            Cost center details with full path
        """
        response = self._get(f"/v1/costcenter/{id}")
        return CostCenterResponse.model_validate(response.json())

    def create(self, cost_center: CreateCostCenter) -> CostCenterCreateResponse:
        """Create a new cost center.

        Args:
            cost_center: Cost center data

        Returns:
            Created cost center ID and active status
        """
        response = self._post("/v1/costcenter", self._model_to_dict(cost_center))
        return CostCenterCreateResponse.model_validate(response.json())

    def update(self, id: int, cost_center: CreateCostCenter) -> None:
        """Update a cost center.

        Args:
            id: Cost center ID
            cost_center: Updated cost center data
        """
        self._patch(f"/v1/costcenter/{id}", self._model_to_dict(cost_center))

    def delete(self, id: int) -> None:
        """Delete a cost center.

        Args:
            id: Cost center ID
        """
        self._delete(f"/v1/costcenter/{id}")

    def iter_all(
        self,
        limit: int = 100,
        **kwargs,
    ) -> Generator[CostCenter, None, None]:
        """Iterate through all cost centers.

        Args:
            limit: Items per page
            **kwargs: Filter parameters

        Yields:
            Individual cost centers
        """
        return self._paginate(
            "/v1/costcenter",
            CostCenterList,
            CostCenter,
            limit=limit,
            **kwargs,
        )
