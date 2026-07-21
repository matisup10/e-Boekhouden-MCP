"""Mutation models for the e-Boekhouden SDK."""

from __future__ import annotations

import datetime
from decimal import Decimal

from pydantic import Field, field_validator

from eboekhouden.models.base import EBoekhoudenModel, PaginatedResponse
from eboekhouden.models.enums import InExVat, MutationType, VatCode


class MutationRow(EBoekhoudenModel):
    """Row in a mutation."""

    ledger_id: int | None = Field(default=None, alias="ledgerId")
    vat_code: str | None = Field(default=None, alias="vatCode")
    vat_amount: Decimal | None = Field(default=None, alias="vatAmount")
    cost_center_id: int | None = Field(default=None, alias="costCenterId")
    amount: Decimal
    description: str | None = None
    invoice_number: str | None = Field(default=None, alias="invoiceNumber")
    relation_id: int | None = Field(default=None, alias="relationId")


class VatAmount(EBoekhoudenModel):
    """VAT amount per code."""

    vat_code: VatCode | str = Field(alias="vatCode")
    amount: Decimal


class MutationListItem(EBoekhoudenModel):
    """Mutation item in list response."""

    id: int
    type: MutationType
    date: datetime.date
    invoice_number: str | None = Field(default=None, alias="invoiceNumber")
    ledger_id: int = Field(alias="ledgerId")
    amount: Decimal
    entry_number: str | None = Field(default=None, alias="entryNumber")

    @field_validator("type", mode="before")
    @classmethod
    def _coerce_type(cls, value):
        return str(value) if isinstance(value, int) else value


class Mutation(EBoekhoudenModel):
    """Full mutation model."""

    id: int
    type: MutationType
    date: datetime.date
    description: str | None = None
    term_of_payment: int | None = Field(default=None, alias="termOfPayment")
    ledger_id: int = Field(alias="ledgerId")
    relation_id: int | None = Field(default=None, alias="relationId")
    in_ex_vat: InExVat | None = Field(default=None, alias="inExVat")
    invoice_number: str | None = Field(default=None, alias="invoiceNumber")
    entry_number: str | None = Field(default=None, alias="entryNumber")
    rows: list[MutationRow] = Field(default_factory=list)
    vat: list[VatAmount] = Field(default_factory=list)

    @field_validator("type", mode="before")
    @classmethod
    def _coerce_type(cls, value):
        return str(value) if isinstance(value, int) else value


class CreateMutationRow(EBoekhoudenModel):
    """Row for creating a mutation."""

    vat_code: VatCode | str = Field(alias="vatCode")
    amount: Decimal
    ledger_id: int | None = Field(default=None, alias="ledgerId")
    vat_amount: Decimal | None = Field(default=None, alias="vatAmount")
    cost_center_id: int | None = Field(default=None, alias="costCenterId")
    description: str | None = None
    invoice_number: str | None = Field(default=None, alias="invoiceNumber")
    relation_id: int | None = Field(default=None, alias="relationId")


class CreateMutation(EBoekhoudenModel):
    """Model for creating a mutation."""

    type: MutationType
    date: datetime.date
    ledger_id: int = Field(alias="ledgerId")
    invoice_number: str | None = Field(
        default=None, alias="invoiceNumber", max_length=50
    )
    entry_number: str | None = Field(default=None, alias="entryNumber", max_length=50)
    term_of_payment: int | None = Field(default=None, alias="termOfPayment")
    check_payment_reference: bool | None = Field(
        default=None, alias="checkPaymentReference"
    )
    payment_reference: str | None = Field(default=None, alias="paymentReference")
    in_ex_vat: InExVat | None = Field(default=None, alias="inExVat")
    description: str | None = Field(default=None, max_length=50)
    relation_id: int | None = Field(default=None, alias="relationId")
    rows: list[CreateMutationRow] | None = None


class CreatedMutation(EBoekhoudenModel):
    """Response from creating a mutation."""

    id: int


class OutstandingInvoice(EBoekhoudenModel):
    """Outstanding invoice in list response."""

    date: datetime.date
    mutation_id: int = Field(alias="mutationId")
    invoice_number: str | None = Field(
        default=None, alias="invoiceNumber"
    )  # Deprecated
    relation_id: int = Field(alias="relationId")
    relation_code: str | None = Field(default=None, alias="relationCode")  # Deprecated
    company: str | None = None
    total_amount: Decimal = Field(alias="totalAmount")
    paid_amount: Decimal = Field(alias="paidAmount")
    outstanding_amount: Decimal = Field(alias="outstandingAmount")


class OutstandingInvoicesList(PaginatedResponse[OutstandingInvoice]):
    """Paginated list of outstanding invoices."""

    pass


class MutationList(PaginatedResponse[MutationListItem]):
    """Paginated list of mutations."""

    pass
