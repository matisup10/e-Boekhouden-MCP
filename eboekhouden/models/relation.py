"""Relation models for the e-Boekhouden SDK."""

from __future__ import annotations

import datetime

from pydantic import Field, field_validator

from eboekhouden.models.base import EBoekhoudenModel, PaginatedResponse
from eboekhouden.models.enums import Gender, MandateType, RelationType


class RelationListItem(EBoekhoudenModel):
    """Relation item in list response."""

    id: int
    type: RelationType | None = None
    code: str | None = None


class Relation(EBoekhoudenModel):
    """Full relation model."""

    id: int
    type: RelationType | None = None
    code: str | None = None
    date: datetime.date | None = None
    name: str

    @field_validator("date", mode="before")
    @classmethod
    def _coerce_date(cls, v):
        if isinstance(v, str) and "T" in v:
            return v.split("T")[0]
        return v

    salutation: str | None = None
    contact: str | None = None
    gender: Gender | None = None
    address: str | None = None
    postal_code: str | None = Field(default=None, alias="postalCode")
    city: str | None = None
    country: str | None = None
    address2: str | None = None
    postal_code2: str | None = Field(default=None, alias="postalCode2")
    city2: str | None = None
    country2: str | None = None
    phone_number: str | None = Field(default=None, alias="phoneNumber")
    mobile_phone_number: str | None = Field(default=None, alias="mobilePhoneNumber")
    fax_number: str | None = Field(default=None, alias="faxNumber")
    email_address: str | None = Field(default=None, alias="emailAddress")
    email_address_invoice: str | None = Field(default=None, alias="emailAddressInvoice")
    email_address_reminder: str | None = Field(
        default=None, alias="emailAddressReminder"
    )
    website: str | None = None
    note: str | None = None
    vat_number: str | None = Field(default=None, alias="vatNumber")
    inactive: bool | None = None
    term_of_payment: int | None = Field(default=None, alias="termOfPayment")
    company_registration_number: str | None = Field(
        default=None, alias="companyRegistrationNumber"
    )
    iban: str | None = None
    bic: str | None = None
    free_text1: str | None = Field(default=None, alias="freeText1")
    free_text2: str | None = Field(default=None, alias="freeText2")
    free_text3: str | None = Field(default=None, alias="freeText3")
    free_text4: str | None = Field(default=None, alias="freeText4")
    free_text5: str | None = Field(default=None, alias="freeText5")
    free_text6: str | None = Field(default=None, alias="freeText6")
    free_text7: str | None = Field(default=None, alias="freeText7")
    free_text8: str | None = Field(default=None, alias="freeText8")
    free_text9: str | None = Field(default=None, alias="freeText9")
    free_text10: str | None = Field(default=None, alias="freeText10")
    do_not_receive_newsletters: int | None = Field(
        default=None, alias="doNotReceiveNewsletters"
    )
    ledger_id: int | None = Field(default=None, alias="ledgerId")
    mandate: bool | None = None
    mandate_type: MandateType | None = Field(default=None, alias="mandateType")
    mandate_id: str | None = Field(default=None, alias="mandateId")
    mandate_signed_date: datetime.date | None = Field(
        default=None, alias="mandateSignedDate"
    )
    peppol_id: str | None = Field(default=None, alias="peppolId")


class CreateRelation(EBoekhoudenModel):
    """Model for creating a relation."""

    name: str = Field(max_length=100)
    type: RelationType | None = None
    code: str | None = Field(default=None, max_length=15)
    salutation: str | None = Field(default=None, max_length=50)
    contact: str | None = Field(default=None, max_length=50)
    gender: Gender | None = None
    address: str | None = Field(default=None, max_length=150)
    postal_code: str | None = Field(default=None, alias="postalCode", max_length=50)
    city: str | None = Field(default=None, max_length=50)
    country: str | None = Field(default=None, max_length=50)
    address2: str | None = Field(default=None, max_length=150)
    postal_code2: str | None = Field(default=None, alias="postalCode2", max_length=50)
    city2: str | None = Field(default=None, max_length=50)
    country2: str | None = Field(default=None, max_length=50)
    phone_number: str | None = Field(default=None, alias="phoneNumber", max_length=50)
    mobile_phone_number: str | None = Field(
        default=None, alias="mobilePhoneNumber", max_length=50
    )
    fax_number: str | None = Field(default=None, alias="faxNumber", max_length=50)
    email_address: str | None = Field(
        default=None, alias="emailAddress", max_length=150
    )
    email_address_invoice: str | None = Field(
        default=None, alias="emailAddressInvoice", max_length=150
    )
    email_address_reminder: str | None = Field(
        default=None, alias="emailAddressReminder", max_length=150
    )
    website: str | None = Field(default=None, max_length=50)
    note: str | None = Field(default=None, max_length=40000)
    vat_number: str | None = Field(default=None, alias="vatNumber", max_length=50)
    inactive: bool | None = None
    term_of_payment: int | None = Field(default=None, alias="termOfPayment")
    company_registration_number: str | None = Field(
        default=None, alias="companyRegistrationNumber", max_length=50
    )
    iban: str | None = Field(default=None, max_length=50)
    bic: str | None = Field(default=None, max_length=20)
    free_text1: str | None = Field(default=None, alias="freeText1", max_length=100)
    free_text2: str | None = Field(default=None, alias="freeText2", max_length=100)
    free_text3: str | None = Field(default=None, alias="freeText3", max_length=100)
    free_text4: str | None = Field(default=None, alias="freeText4", max_length=100)
    free_text5: str | None = Field(default=None, alias="freeText5", max_length=100)
    free_text6: str | None = Field(default=None, alias="freeText6", max_length=100)
    free_text7: str | None = Field(default=None, alias="freeText7", max_length=100)
    free_text8: str | None = Field(default=None, alias="freeText8", max_length=100)
    free_text9: str | None = Field(default=None, alias="freeText9", max_length=100)
    free_text10: str | None = Field(default=None, alias="freeText10", max_length=100)
    do_not_receive_newsletters: bool | None = Field(
        default=None, alias="doNotReceiveNewsletters"
    )
    ledger_id: int | None = Field(default=None, alias="ledgerId")
    mandate: bool | None = None
    mandate_type: MandateType | None = Field(default=None, alias="mandateType")
    mandate_id: str | None = Field(default=None, alias="mandateId", max_length=35)
    mandate_signed_date: datetime.date | None = Field(
        default=None, alias="mandateSignedDate"
    )
    peppol_id: str | None = Field(default=None, alias="peppolId")


class PatchRelation(CreateRelation):
    """Model for updating a relation (same fields as create, all optional except name)."""

    pass


class CreatedRelation(EBoekhoudenModel):
    """Response from creating a relation."""

    id: int
    code: str


class RelationList(PaginatedResponse[RelationListItem]):
    """Paginated list of relations."""

    pass
