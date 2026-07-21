"""Relation tools for the e-Boekhouden MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import Field

from eboekhouden.models.relation import CreateRelation, PatchRelation
from eboekhouden_mcp.tools.base import BaseTool, PaginatedInput, ToolSchema

if TYPE_CHECKING:
    from eboekhouden import EBoekhoudenClient


class ListRelationsInput(PaginatedInput):
    """Input schema for list_relations tool."""

    code: str | None = Field(default=None, description="Filter by relation code")
    type: str | None = Field(
        default=None, description="Filter by type ('B' for business or 'P' for private)"
    )
    email: str | None = Field(default=None, description="Filter by email address")
    name: str | None = Field(default=None, description="Filter by company name")
    contact: str | None = Field(default=None, description="Filter by contact name")
    city: str | None = Field(default=None, description="Filter by city")


class ListRelationsTool(BaseTool):
    """List all relations (customers/suppliers)."""

    name = "list_relations"
    description = "List all relations (customers and suppliers) with optional filters for code, type, name, email, city, etc."
    input_schema = ListRelationsInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        result = client.relations.list(
            limit=arguments.get("limit"),
            offset=arguments.get("offset"),
            code=arguments.get("code"),
            type=arguments.get("type"),
            email=arguments.get("email"),
            name=arguments.get("name"),
            contact=arguments.get("contact"),
            city=arguments.get("city"),
        )
        return {
            "count": result.count,
            "items": [item.model_dump() for item in result.items],
        }


class GetRelationInput(ToolSchema):
    """Input schema for get_relation tool."""

    id: int = Field(description="Relation ID")


class GetRelationTool(BaseTool):
    """Get a relation by ID."""

    name = "get_relation"
    description = "Get full details of a relation (customer/supplier) by ID, including contact info, address, VAT number, etc."
    input_schema = GetRelationInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        relation = client.relations.get(arguments["id"])
        return relation.model_dump()


class CreateRelationInput(ToolSchema):
    """Input schema for create_relation tool."""

    name: str = Field(description="Company or contact name (required, max 100 chars)")
    type: str | None = Field(
        default=None, description="Type: 'B' for business or 'P' for private"
    )
    code: str | None = Field(default=None, description="Relation code (max 15 chars)")
    salutation: str | None = Field(
        default=None, description="Salutation (max 50 chars)"
    )
    contact: str | None = Field(
        default=None, description="Contact person (max 50 chars)"
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
    website: str | None = Field(default=None, description="Website URL (max 50 chars)")
    vat_number: str | None = Field(
        default=None, description="VAT number (max 50 chars)"
    )
    iban: str | None = Field(default=None, description="IBAN (max 50 chars)")
    note: str | None = Field(default=None, description="Notes (max 40000 chars)")
    term_of_payment: int | None = Field(
        default=None, description="Default payment term in days"
    )


class CreateRelationTool(BaseTool):
    """Create a new relation."""

    name = "create_relation"
    description = "Create a new relation (customer/supplier) with name, address, contact info, etc."
    input_schema = CreateRelationInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        relation_data = CreateRelation(
            name=arguments["name"],
            type=arguments.get("type"),
            code=arguments.get("code"),
            salutation=arguments.get("salutation"),
            contact=arguments.get("contact"),
            gender=arguments.get("gender"),
            address=arguments.get("address"),
            postal_code=arguments.get("postal_code"),
            city=arguments.get("city"),
            country=arguments.get("country"),
            phone_number=arguments.get("phone_number"),
            email_address=arguments.get("email_address"),
            website=arguments.get("website"),
            vat_number=arguments.get("vat_number"),
            iban=arguments.get("iban"),
            note=arguments.get("note"),
            term_of_payment=arguments.get("term_of_payment"),
        )
        result = client.relations.create(relation_data)
        return {"id": result.id, "code": result.code}


class UpdateRelationInput(ToolSchema):
    """Input schema for update_relation tool."""

    id: int = Field(description="Relation ID to update")
    name: str = Field(description="Company or contact name (required)")
    type: str | None = Field(
        default=None, description="Type: 'B' for business or 'P' for private"
    )
    code: str | None = Field(default=None, description="Relation code")
    contact: str | None = Field(default=None, description="Contact person")
    address: str | None = Field(default=None, description="Street address")
    postal_code: str | None = Field(default=None, description="Postal code")
    city: str | None = Field(default=None, description="City")
    country: str | None = Field(default=None, description="Country")
    phone_number: str | None = Field(default=None, description="Phone number")
    email_address: str | None = Field(default=None, description="Email address")
    vat_number: str | None = Field(default=None, description="VAT number")
    iban: str | None = Field(default=None, description="IBAN")
    inactive: bool | None = Field(default=None, description="Mark as inactive")


class UpdateRelationTool(BaseTool):
    """Update an existing relation."""

    name = "update_relation"
    description = (
        "Update an existing relation's details like name, address, contact info, etc."
    )
    input_schema = UpdateRelationInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        relation_id = arguments.pop("id")
        relation_data = PatchRelation(
            name=arguments["name"],
            type=arguments.get("type"),
            code=arguments.get("code"),
            contact=arguments.get("contact"),
            address=arguments.get("address"),
            postal_code=arguments.get("postal_code"),
            city=arguments.get("city"),
            country=arguments.get("country"),
            phone_number=arguments.get("phone_number"),
            email_address=arguments.get("email_address"),
            vat_number=arguments.get("vat_number"),
            iban=arguments.get("iban"),
            inactive=arguments.get("inactive"),
        )
        client.relations.update(relation_id, relation_data)
        return {"success": True, "id": relation_id}


class DeleteRelationInput(ToolSchema):
    """Input schema for delete_relation tool."""

    id: int = Field(description="Relation ID to delete")


class DeleteRelationTool(BaseTool):
    """Delete a relation."""

    name = "delete_relation"
    description = "Delete a relation (customer/supplier) by ID"
    input_schema = DeleteRelationInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        client.relations.delete(arguments["id"])
        return {"success": True, "id": arguments["id"]}
