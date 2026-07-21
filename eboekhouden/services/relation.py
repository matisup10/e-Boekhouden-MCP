"""Relation service for the e-Boekhouden SDK."""

from typing import Generator

from eboekhouden.filters import Filter
from eboekhouden.models.relation import (
    CreateRelation,
    CreatedRelation,
    PatchRelation,
    Relation,
    RelationList,
    RelationListItem,
)
from eboekhouden.services.base import BaseService


class RelationService(BaseService):
    """Service for relation endpoints."""

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        code: str | Filter | None = None,
        type: str | Filter | None = None,
        email: str | Filter | None = None,
        name: str | Filter | None = None,
        contact: str | Filter | None = None,
        city: str | Filter | None = None,
    ) -> RelationList:
        """Get all relations.

        Args:
            limit: Number of items to retrieve (max 2000)
            offset: Number of items to skip
            code: Filter by relation code
            type: Filter by type ('B' or 'P')
            email: Filter by email address
            name: Filter by company name
            contact: Filter by contact name
            city: Filter by city

        Returns:
            Paginated list of relations
        """
        params = self._build_params(
            limit=limit,
            offset=offset,
            code=code,
            type=type,
            email=email,
            name=name,
            contact=contact,
            city=city,
        )
        response = self._get("/v1/relation", params)
        return RelationList.model_validate(response.json())

    def get(self, id: int) -> Relation:
        """Get a relation by ID.

        Args:
            id: Relation ID

        Returns:
            Full relation details
        """
        response = self._get(f"/v1/relation/{id}")
        return Relation.model_validate(response.json())

    def create(self, relation: CreateRelation) -> CreatedRelation:
        """Create a new relation.

        Args:
            relation: Relation data

        Returns:
            Created relation ID and code
        """
        response = self._post("/v1/relation", self._model_to_dict(relation))
        return CreatedRelation.model_validate(response.json())

    def update(self, id: int, relation: PatchRelation) -> None:
        """Update a relation.

        Args:
            id: Relation ID
            relation: Updated relation data
        """
        self._patch(f"/v1/relation/{id}", self._model_to_dict(relation))

    def delete(self, id: int) -> None:
        """Delete a relation.

        Args:
            id: Relation ID
        """
        self._delete(f"/v1/relation/{id}")

    def iter_all(
        self, limit: int = 100, **kwargs
    ) -> Generator[RelationListItem, None, None]:
        """Iterate through all relations.

        Args:
            limit: Items per page
            **kwargs: Filter parameters

        Yields:
            Individual relations
        """
        return self._paginate(
            "/v1/relation",
            RelationList,
            RelationListItem,
            limit=limit,
            **kwargs,
        )
