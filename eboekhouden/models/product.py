"""Product models for the e-Boekhouden SDK."""

from __future__ import annotations

from decimal import Decimal

from pydantic import Field

from eboekhouden.models.base import EBoekhoudenModel, PaginatedResponse
from eboekhouden.models.enums import VatCode


class ProductListItem(EBoekhoudenModel):
    """Product item in list response."""

    id: int
    code: str
    description: str
    unit_id: int | None = Field(default=None, alias="unitId")
    active: bool


class Product(EBoekhoudenModel):
    """Full product model."""

    id: int
    code: str
    description: str
    unit_id: int | None = Field(default=None, alias="unitId")
    ledger_id: int = Field(alias="ledgerId")
    vat_code: VatCode | str = Field(alias="vatCode")
    price_excl: Decimal | None = Field(default=None, alias="priceExcl")
    price_incl: Decimal | None = Field(default=None, alias="priceIncl")
    purchase_price_excl: Decimal | None = Field(default=None, alias="purchasePriceExcl")
    cost_center_id: int | None = Field(default=None, alias="costCenterId")
    group_code: str | None = Field(default=None, alias="groupCode")
    active: bool


class CreateProduct(EBoekhoudenModel):
    """Model for creating a product."""

    code: str
    description: str
    ledger_id: int = Field(alias="ledgerId")
    vat_code: VatCode | str = Field(alias="vatCode")
    unit_id: int | None = Field(default=None, alias="unitId")
    price_excl: Decimal | None = Field(default=None, alias="priceExcl")
    price_incl: Decimal | None = Field(default=None, alias="priceIncl")
    purchase_price_excl: Decimal | None = Field(default=None, alias="purchasePriceExcl")
    cost_center_id: int | None = Field(default=None, alias="costCenterId")
    group_code: str | None = Field(default=None, alias="groupCode")
    active: bool = True


class PatchProduct(EBoekhoudenModel):
    """Model for updating a product."""

    code: str | None = None
    description: str | None = None
    ledger_id: int | None = Field(default=None, alias="ledgerId")
    vat_code: VatCode | str | None = Field(default=None, alias="vatCode")
    unit_id: int | None = Field(default=None, alias="unitId")
    price_excl: Decimal | None = Field(default=None, alias="priceExcl")
    price_incl: Decimal | None = Field(default=None, alias="priceIncl")
    purchase_price_excl: Decimal | None = Field(default=None, alias="purchasePriceExcl")
    cost_center_id: int | None = Field(default=None, alias="costCenterId")
    group_code: str | None = Field(default=None, alias="groupCode")
    active: bool | None = None
    update_subscriptions: int | None = Field(default=None, alias="updateSubscriptions")


class CreatedProduct(EBoekhoudenModel):
    """Response from creating a product."""

    id: int


class ProductGroup(EBoekhoudenModel):
    """Product group model."""

    code: str
    description: str


class ProductGroupList(PaginatedResponse[ProductGroup]):
    """Paginated list of product groups."""

    pass


class ProductList(PaginatedResponse[ProductListItem]):
    """Paginated list of products."""

    pass
