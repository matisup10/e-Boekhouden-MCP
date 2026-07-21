"""Member service for the e-Boekhouden SDK."""

from typing import Generator

from eboekhouden.filters import Filter
from eboekhouden.models.member import (
    CreateMember,
    CreatedMember,
    Member,
    MemberList,
    MemberListItem,
)
from eboekhouden.services.base import BaseService


class MemberService(BaseService):
    """Service for member endpoints (only for clubs/associations)."""

    def list(
        self,
        *,
        limit: int | None = None,
        offset: int | None = None,
        member_number: str | Filter | None = None,
        name: str | Filter | None = None,
        email: str | Filter | None = None,
        city: str | Filter | None = None,
    ) -> MemberList:
        """Get all members.

        Args:
            limit: Number of items to retrieve (max 2000)
            offset: Number of items to skip
            member_number: Filter by member number
            name: Filter by name
            email: Filter by email
            city: Filter by city

        Returns:
            Paginated list of members
        """
        params = self._build_params(
            limit=limit,
            offset=offset,
            memberNumber=member_number,
            name=name,
            email=email,
            city=city,
        )
        response = self._get("/v1/member", params)
        return MemberList.model_validate(response.json())

    def get(self, id: int) -> Member:
        """Get a member by ID.

        Args:
            id: Member ID

        Returns:
            Full member details
        """
        response = self._get(f"/v1/member/{id}")
        return Member.model_validate(response.json())

    def create(self, member: CreateMember) -> CreatedMember:
        """Create a new member.

        Args:
            member: Member data

        Returns:
            Created member ID and number
        """
        response = self._post("/v1/member", self._model_to_dict(member))
        return CreatedMember.model_validate(response.json())

    def update(self, id: int, member: CreateMember) -> None:
        """Update a member.

        Args:
            id: Member ID
            member: Updated member data
        """
        self._patch(f"/v1/member/{id}", self._model_to_dict(member))

    def delete(self, id: int) -> None:
        """Delete a member.

        Args:
            id: Member ID
        """
        self._delete(f"/v1/member/{id}")

    def iter_all(
        self, limit: int = 100, **kwargs
    ) -> Generator[MemberListItem, None, None]:
        """Iterate through all members.

        Args:
            limit: Items per page
            **kwargs: Filter parameters

        Yields:
            Individual members
        """
        return self._paginate(
            "/v1/member",
            MemberList,
            MemberListItem,
            limit=limit,
            **kwargs,
        )
