"""Member models for the e-Boekhouden SDK."""

from __future__ import annotations

import datetime

from pydantic import Field

from eboekhouden.models.base import EBoekhoudenModel, PaginatedResponse
from eboekhouden.models.enums import Gender, MandateType


class MemberListItem(EBoekhoudenModel):
    """Member item in list response."""

    id: int
    member_number: str | None = Field(default=None, alias="memberNumber")
    name: str


class Member(EBoekhoudenModel):
    """Full member model."""

    id: int
    member_number: str | None = Field(default=None, alias="memberNumber")
    name: str
    salutation: str | None = None
    gender: Gender | None = None
    address: str | None = None
    postal_code: str | None = Field(default=None, alias="postalCode")
    city: str | None = None
    country: str | None = None
    phone_number: str | None = Field(default=None, alias="phoneNumber")
    mobile_phone_number: str | None = Field(default=None, alias="mobilePhoneNumber")
    fax_number: str | None = Field(default=None, alias="faxNumber")
    email_address: str | None = Field(default=None, alias="emailAddress")
    email_address_invoice: str | None = Field(default=None, alias="emailAddressInvoice")
    email_address_reminder: str | None = Field(
        default=None, alias="emailAddressReminder"
    )
    note: str | None = None
    term_of_payment: int | None = Field(default=None, alias="termOfPayment")
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


class CreateMember(EBoekhoudenModel):
    """Model for creating a member."""

    name: str = Field(max_length=100)
    member_number: str | None = Field(default=None, alias="memberNumber", max_length=15)
    salutation: str | None = Field(default=None, max_length=50)
    gender: Gender | None = None
    address: str | None = Field(default=None, max_length=150)
    postal_code: str | None = Field(default=None, alias="postalCode", max_length=50)
    city: str | None = Field(default=None, max_length=50)
    country: str | None = Field(default=None, max_length=50)
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
    note: str | None = Field(default=None, max_length=40000)
    term_of_payment: int | None = Field(default=None, alias="termOfPayment")
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


class CreatedMember(EBoekhoudenModel):
    """Response from creating a member."""

    id: int
    member_number: str = Field(alias="memberNumber")


class MemberList(PaginatedResponse[MemberListItem]):
    """Paginated list of members."""

    pass
