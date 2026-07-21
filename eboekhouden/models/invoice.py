"""Invoice models for the e-Boekhouden SDK."""

from __future__ import annotations

import datetime
from decimal import Decimal

from pydantic import Field

from eboekhouden.models.base import EBoekhoudenModel, PaginatedResponse
from eboekhouden.models.enums import InExVat, VatCode


class InvoiceItem(EBoekhoudenModel):
    """Invoice line item."""

    quantity: Decimal | None = None
    amount: Decimal | None = None  # Deprecated, use quantity
    unit_id: int | None = Field(default=None, alias="unitId")
    code: str | None = None
    product_id: int | None = Field(default=None, alias="productId")
    description: str
    price_per_unit: Decimal | None = Field(default=None, alias="pricePerUnit")
    vat_code: VatCode | str = Field(alias="vatCode")
    vat_amount: Decimal | None = Field(default=None, alias="vatAmount")
    ledger_id: int = Field(alias="ledgerId")
    cost_center_id: int | None = Field(default=None, alias="costCenterId")
    discount_amount: Decimal | None = Field(default=None, alias="discountAmount")
    discount_percentage: Decimal | None = Field(
        default=None, alias="discountPercentage"
    )


class InvoiceListItem(EBoekhoudenModel):
    """Invoice item in list response."""

    id: int
    invoice_number: str = Field(alias="invoiceNumber")
    relation_id: int = Field(alias="relationId")
    date: datetime.date
    reference: str | None = None
    text: str | None = None
    url_pdf_file: str | None = Field(default=None, alias="urlPdfFile")
    total_excl: Decimal = Field(alias="totalExcl")
    total_amount: Decimal = Field(alias="totalAmount")
    vat_amount: Decimal = Field(alias="vatAmount")
    term_of_payment: int = Field(alias="termOfPayment")
    template_id: int = Field(alias="templateId")
    print: bool = False


class Invoice(EBoekhoudenModel):
    """Full invoice model."""

    id: int
    invoice_number: str = Field(alias="invoiceNumber")
    relation_id: int = Field(alias="relationId")
    date: datetime.date
    reference: str | None = None
    text: str | None = None
    term_of_payment: int = Field(alias="termOfPayment")
    in_ex_vat: InExVat | None = Field(default=None, alias="inExVat")
    template_id: int = Field(alias="templateId")
    email_template_id: int | None = Field(default=None, alias="emailTemplateId")
    total_excl: Decimal = Field(alias="totalExcl")
    total_amount: Decimal = Field(alias="totalAmount")
    vat_amount: Decimal = Field(alias="vatAmount")
    url_pdf_file: str | None = Field(default=None, alias="urlPdfFile")
    items: list[InvoiceItem] = []


class CreateInvoiceItem(EBoekhoudenModel):
    """Invoice line item for creation."""

    description: str
    vat_code: VatCode | str = Field(alias="vatCode")
    ledger_id: int = Field(alias="ledgerId")
    quantity: Decimal | None = None
    unit_id: int | None = Field(default=None, alias="unitId")
    code: str | None = Field(default=None, max_length=50)
    product_id: int | None = Field(default=None, alias="productId")
    price_per_unit: Decimal | None = Field(default=None, alias="pricePerUnit")
    vat_amount: Decimal | None = Field(default=None, alias="vatAmount")
    cost_center_id: int | None = Field(default=None, alias="costCenterId")
    discount_amount: Decimal | None = Field(default=None, alias="discountAmount")
    discount_percentage: Decimal | None = Field(
        default=None, alias="discountPercentage"
    )


class CreateInvoiceEmail(EBoekhoudenModel):
    """Email options for sending invoice."""

    from_email: str | None = Field(default=None, alias="fromEmail")
    from_name: str | None = Field(default=None, alias="fromName")
    subject: str | None = None
    body: str | None = None
    attach_ubl: bool = Field(default=False, alias="attachUbl")


class CreateInvoiceDebit(EBoekhoudenModel):
    """Direct debit options for invoice."""

    iban: str = Field(max_length=150)
    mandate_type: str | None = Field(default=None, alias="mandateType")  # O, E, R, D
    mandate_id: str | None = Field(default=None, alias="mandateId", max_length=35)
    mandate_signed_date: datetime.date | None = Field(
        default=None, alias="mandateSignedDate"
    )
    name: str | None = Field(default=None, max_length=150)
    city: str | None = Field(default=None, max_length=150)
    description_line1: str | None = Field(
        default=None, alias="descriptionLine1", max_length=50
    )
    description_line2: str | None = Field(
        default=None, alias="descriptionLine2", max_length=50
    )
    description_line3: str | None = Field(
        default=None, alias="descriptionLine3", max_length=50
    )


class CreateInvoiceMutation(EBoekhoudenModel):
    """Options for automatically creating a mutation from the invoice."""

    description: str | None = Field(default=None, max_length=200)
    check_payment_reference: bool | None = Field(
        default=None, alias="checkPaymentReference"
    )
    payment_reference: str | None = Field(
        default=None, alias="paymentReference", max_length=50
    )
    ledger_id: int | None = Field(default=None, alias="ledgerId")


class CreateInvoice(EBoekhoudenModel):
    """Model for creating an invoice."""

    relation_id: int = Field(alias="relationId")
    term_of_payment: int = Field(alias="termOfPayment")
    template_id: int = Field(alias="templateId")
    items: list[CreateInvoiceItem]
    invoice_number: str | None = Field(
        default=None, alias="invoiceNumber", max_length=50
    )
    date: datetime.date | None = None
    in_ex_vat: InExVat | None = Field(default=None, alias="inExVat")
    email_template_id: int | None = Field(default=None, alias="emailTemplateId")
    reference: str | None = Field(default=None, max_length=50)
    text: str | None = Field(default=None, max_length=35000)
    print: bool | None = None
    email: CreateInvoiceEmail | None = None
    direct_debit: CreateInvoiceDebit | None = Field(default=None, alias="directDebit")
    mutation: CreateInvoiceMutation | None = None


class CreatedInvoice(EBoekhoudenModel):
    """Response from creating an invoice."""

    id: int
    invoice_number: str = Field(alias="invoiceNumber")
    in_ex_vat: InExVat | None = Field(default=None, alias="inExVat")


class InvoiceList(PaginatedResponse[InvoiceListItem]):
    """Paginated list of invoices."""

    pass
