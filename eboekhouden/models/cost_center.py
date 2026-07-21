"""Cost center models for the e-Boekhouden SDK."""

from __future__ import annotations

from pydantic import Field

from eboekhouden.models.base import EBoekhoudenModel, PaginatedResponse


class CostCenter(EBoekhoudenModel):
    """Cost center model for list responses."""

    id: int
    description: str
    parent_id: int | None = Field(default=None, alias="parentId")
    active: bool


class CostCenterResponse(CostCenter):
    """Cost center model with full path (from GET by id)."""

    full_path: str | None = Field(default=None, alias="fullPath")


class CreateCostCenter(EBoekhoudenModel):
    """Model for creating a cost center."""

    description: str = Field(max_length=50)
    parent_id: int | None = Field(default=None, alias="parentId")
    active: bool = True


class CostCenterCreateResponse(EBoekhoudenModel):
    """Response from creating a cost center."""

    id: int
    active: bool


class CostCenterList(PaginatedResponse[CostCenter]):
    """Paginated list of cost centers."""

    pass
