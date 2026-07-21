"""Product tools for the e-Boekhouden MCP server."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import Field

from eboekhouden.models.product import CreateProduct, PatchProduct
from eboekhouden_mcp.tools.base import BaseTool, ToolSchema

if TYPE_CHECKING:
    from eboekhouden import EBoekhoudenClient


class ListProductsInput(ToolSchema):
    """Input schema for list_products tool."""

    limit: int | None = Field(
        default=None, description="Number of items to retrieve (max 2000)"
    )
    offset: int | None = Field(default=None, description="Number of items to skip")
    code: str | None = Field(default=None, description="Filter by product code")
    group_code: str | None = Field(
        default=None, description="Filter by product group code"
    )


class ListProductsTool(BaseTool):
    """List all products."""

    name = "list_products"
    description = (
        "List all products in the catalog with optional filters for code and group"
    )
    input_schema = ListProductsInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        result = client.products.list(
            limit=arguments.get("limit"),
            offset=arguments.get("offset"),
            code=arguments.get("code"),
            group_code=arguments.get("group_code"),
        )
        return {
            "count": result.count,
            "items": [item.model_dump() for item in result.items],
        }


class GetProductInput(ToolSchema):
    """Input schema for get_product tool."""

    id: int = Field(description="Product ID")


class GetProductTool(BaseTool):
    """Get a product by ID."""

    name = "get_product"
    description = "Get full details of a product by ID, including price, VAT code, ledger, and unit"
    input_schema = GetProductInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        product = client.products.get(arguments["id"])
        return product.model_dump()


class CreateProductInput(ToolSchema):
    """Input schema for create_product tool."""

    code: str = Field(description="Product code (max 50 chars)")
    description: str = Field(description="Product description (max 200 chars)")
    vat_code: str = Field(description="VAT code (e.g., 'HOOG_VERK_21')")
    ledger_id: int = Field(description="Ledger account ID for revenue")
    price_excl: float | None = Field(default=None, description="Price excluding VAT")
    price_incl: float | None = Field(default=None, description="Price including VAT")
    purchase_price_excl: float | None = Field(
        default=None, description="Purchase price excluding VAT"
    )
    unit_id: int | None = Field(default=None, description="Unit of measurement ID")
    group_code: str | None = Field(default=None, description="Product group code")
    cost_center_id: int | None = Field(
        default=None, description="Default cost center ID"
    )
    active: bool | None = Field(default=True, description="Whether product is active")


class CreateProductTool(BaseTool):
    """Create a new product."""

    name = "create_product"
    description = "Create a new product in the catalog with code, description, price, VAT code, and ledger"
    input_schema = CreateProductInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        product_data = CreateProduct(
            code=arguments["code"],
            description=arguments["description"],
            vat_code=arguments["vat_code"],
            ledger_id=arguments["ledger_id"],
            price_excl=arguments.get("price_excl"),
            price_incl=arguments.get("price_incl"),
            purchase_price_excl=arguments.get("purchase_price_excl"),
            unit_id=arguments.get("unit_id"),
            group_code=arguments.get("group_code"),
            cost_center_id=arguments.get("cost_center_id"),
            active=arguments.get("active", True),
        )
        result = client.products.create(product_data)
        return {"id": result.id}


class UpdateProductInput(ToolSchema):
    """Input schema for update_product tool."""

    id: int = Field(description="Product ID to update")
    code: str | None = Field(default=None, description="Product code")
    description: str | None = Field(default=None, description="Product description")
    vat_code: str | None = Field(default=None, description="VAT code")
    ledger_id: int | None = Field(default=None, description="Ledger account ID")
    price_excl: float | None = Field(default=None, description="Price excluding VAT")
    price_incl: float | None = Field(default=None, description="Price including VAT")
    unit_id: int | None = Field(default=None, description="Unit of measurement ID")
    group_code: str | None = Field(default=None, description="Product group code")
    active: bool | None = Field(default=None, description="Whether product is active")


class UpdateProductTool(BaseTool):
    """Update an existing product."""

    name = "update_product"
    description = "Update an existing product's details like code, description, price, or active status"
    input_schema = UpdateProductInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        product_id = arguments.pop("id")
        product_data = PatchProduct(
            code=arguments.get("code"),
            description=arguments.get("description"),
            vat_code=arguments.get("vat_code"),
            ledger_id=arguments.get("ledger_id"),
            price_excl=arguments.get("price_excl"),
            price_incl=arguments.get("price_incl"),
            unit_id=arguments.get("unit_id"),
            group_code=arguments.get("group_code"),
            active=arguments.get("active"),
        )
        client.products.update(product_id, product_data)
        return {"success": True, "id": product_id}


class DeleteProductInput(ToolSchema):
    """Input schema for delete_product tool."""

    id: int = Field(description="Product ID to delete")


class DeleteProductTool(BaseTool):
    """Delete a product."""

    name = "delete_product"
    description = "Delete a product from the catalog by ID"
    input_schema = DeleteProductInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        client.products.delete(arguments["id"])
        return {"success": True, "id": arguments["id"]}


class ListProductGroupsInput(ToolSchema):
    """Input schema for list_product_groups tool."""

    limit: int | None = Field(
        default=None, description="Number of items to retrieve (max 2000)"
    )
    offset: int | None = Field(default=None, description="Number of items to skip")


class ListProductGroupsTool(BaseTool):
    """List all product groups."""

    name = "list_product_groups"
    description = "List all product groups used to categorize products"
    input_schema = ListProductGroupsInput

    async def execute(
        self, client: "EBoekhoudenClient", arguments: dict[str, Any]
    ) -> dict[str, Any]:
        result = client.products.list_groups(
            limit=arguments.get("limit"),
            offset=arguments.get("offset"),
        )
        return {
            "count": result.count,
            "items": [item.model_dump() for item in result.items],
        }
