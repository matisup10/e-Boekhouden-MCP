"""Member tools for the e-Boekhouden MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import Field

from eboekhouden.models.member import CreateMember
from eboekhouden_mcp.tools.base import BaseTool, PaginatedInput, ToolSchema

if TYPE_CHECKING:
    from eboekhouden import EBoekhoudenClient


class ListMembersInput(PaginatedInput):
    """Input schema for list_members tool."""

    member_number: str | None = Field(
        default=None, description="Filter by member number"
    )
    name: str | None = Field(default=None, description="Filter by name")
    email: str | None = Field(default=None, description="Filter by email")
    city: str | None = Field(default=None, description="Filter by city")


class ListMembersTool(BaseTool):
    """List all members (for clubs/associations)."""

    name = "list_members"
    description = "List all members (for clubs/associations) with optional filters for member number, name, email, city"
    input_schema = ListMembersInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        result = client.members.list(
            limit=arguments.get("limit"),
            offset=arguments.get("offset"),
            member_number=arguments.get("member_number"),
            name=arguments.get("name"),
            email=arguments.get("email"),
            city=arguments.get("city"),
        )
        return {
            "count": result.count,
            "items": [item.model_dump() for item in result.items],
        }


class GetMemberInput(ToolSchema):
    """Input schema for get_member tool."""

    id: int = Field(description="Member ID")


class GetMemberTool(BaseTool):
    """Get a member by ID."""

    name = "get_member"
    description = "Get full details of a member by ID (for clubs/associations)"
    input_schema = GetMemberInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        member = client.members.get(arguments["id"])
        return member.model_dump()


class CreateMemberInput(ToolSchema):
    """Input schema for create_member tool."""

    name: str = Field(description="Member name (required, max 100 chars)")
    member_number: str | None = Field(
        default=None, description="Member number (max 15 chars)"
    )
    salutation: str | None = Field(
        default=None, description="Salutation (max 50 chars)"
    )
    gender: str | None = Field(
        default=None,
        description="Gender: 'm' for male, 'v' for female, 'a' for department",
    )
    address: str | None = Field(
        default=None, description="Street address (max 150 chars)"
    )
    postal_code: str | None = Field(
        default=None, description="Postal code (max 50 chars)"
    )
    city: str | None = Field(default=None, description="City (max 50 chars)")
    country: str | None = Field(default=None, description="Country (max 50 chars)")
    phone_number: str | None = Field(
        default=None, description="Phone number (max 50 chars)"
    )
    email_address: str | None = Field(
        default=None, description="Email address (max 150 chars)"
    )
    note: str | None = Field(default=None, description="Notes (max 40000 chars)")
    iban: str | None = Field(default=None, description="IBAN (max 50 chars)")


class CreateMemberTool(BaseTool):
    """Create a new member."""

    name = "create_member"
    description = (
        "Create a new member (for clubs/associations) with name and contact info"
    )
    input_schema = CreateMemberInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        member_data = CreateMember(
            name=arguments["name"],
            member_number=arguments.get("member_number"),
            salutation=arguments.get("salutation"),
            gender=arguments.get("gender"),
            address=arguments.get("address"),
            postal_code=arguments.get("postal_code"),
            city=arguments.get("city"),
            country=arguments.get("country"),
            phone_number=arguments.get("phone_number"),
            email_address=arguments.get("email_address"),
            note=arguments.get("note"),
            iban=arguments.get("iban"),
        )
        result = client.members.create(member_data)
        return {"id": result.id, "member_number": result.member_number}


class DeleteMemberInput(ToolSchema):
    """Input schema for delete_member tool."""

    id: int = Field(description="Member ID to delete")


class DeleteMemberTool(BaseTool):
    """Delete a member."""

    name = "delete_member"
    description = "Delete a member by ID (for clubs/associations)"
    input_schema = DeleteMemberInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        client.members.delete(arguments["id"])
        return {"success": True, "id": arguments["id"]}
