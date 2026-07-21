"""Base models for the e-Boekhouden SDK."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict


class EBoekhoudenModel(BaseModel):
    """Base model with common configuration for all e-Boekhouden models."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        extra="ignore",
    )


T = TypeVar("T")


class PaginatedResponse(EBoekhoudenModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T]
    count: int
