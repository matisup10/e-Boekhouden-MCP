"""Models for the e-Boekhouden SDK."""

from eboekhouden.models.base import EBoekhoudenModel, PaginatedResponse
from eboekhouden.models.enums import (
    Gender,
    InExVat,
    LedgerCategory,
    MandateType,
    MutationType,
    RelationType,
    VatCode,
)
from eboekhouden.models.session import SessionRequest, SessionResponse
from eboekhouden.models.administration import AdministrationListItem, AdministrationList
from eboekhouden.models.cost_center import (
    CostCenter,
    CostCenterResponse,
    CreateCostCenter,
    CostCenterList,
    CostCenterCreateResponse,
)
from eboekhouden.models.email_template import EmailTemplateListItem, EmailTemplateList
from eboekhouden.models.invoice_template import (
    InvoiceTemplateListItem,
    InvoiceTemplateList,
)
from eboekhouden.models.ledger import (
    Ledger,
    LedgerListItem,
    LedgerList,
    LedgerBalance,
    CreateLedger,
    PatchLedger,
)
from eboekhouden.models.relation import (
    Relation,
    RelationListItem,
    RelationList,
    CreateRelation,
    PatchRelation,
    CreatedRelation,
)
from eboekhouden.models.invoice import (
    Invoice,
    InvoiceItem,
    InvoiceListItem,
    InvoiceList,
    CreateInvoice,
    CreateInvoiceItem,
    CreateInvoiceEmail,
    CreateInvoiceDebit,
    CreateInvoiceMutation,
    CreatedInvoice,
)
from eboekhouden.models.mutation import (
    Mutation,
    MutationRow,
    MutationListItem,
    MutationList,
    CreateMutation,
    CreateMutationRow,
    CreatedMutation,
    OutstandingInvoice,
    OutstandingInvoicesList,
    VatAmount,
)
from eboekhouden.models.product import (
    Product,
    ProductListItem,
    ProductList,
    CreateProduct,
    PatchProduct,
    CreatedProduct,
    ProductGroup,
    ProductGroupList,
)
from eboekhouden.models.member import (
    Member,
    MemberListItem,
    MemberList,
    CreateMember,
    CreatedMember,
)
from eboekhouden.models.unit import Unit, UnitList

__all__ = [
    # Base
    "EBoekhoudenModel",
    "PaginatedResponse",
    # Enums
    "Gender",
    "InExVat",
    "LedgerCategory",
    "MandateType",
    "MutationType",
    "RelationType",
    "VatCode",
    # Session
    "SessionRequest",
    "SessionResponse",
    # Administration
    "AdministrationListItem",
    "AdministrationList",
    # Cost Center
    "CostCenter",
    "CostCenterResponse",
    "CreateCostCenter",
    "CostCenterList",
    "CostCenterCreateResponse",
    # Email Template
    "EmailTemplateListItem",
    "EmailTemplateList",
    # Invoice Template
    "InvoiceTemplateListItem",
    "InvoiceTemplateList",
    # Ledger
    "Ledger",
    "LedgerListItem",
    "LedgerList",
    "LedgerBalance",
    "CreateLedger",
    "PatchLedger",
    # Relation
    "Relation",
    "RelationListItem",
    "RelationList",
    "CreateRelation",
    "PatchRelation",
    "CreatedRelation",
    # Invoice
    "Invoice",
    "InvoiceItem",
    "InvoiceListItem",
    "InvoiceList",
    "CreateInvoice",
    "CreateInvoiceItem",
    "CreateInvoiceEmail",
    "CreateInvoiceDebit",
    "CreateInvoiceMutation",
    "CreatedInvoice",
    # Mutation
    "Mutation",
    "MutationRow",
    "MutationListItem",
    "MutationList",
    "CreateMutation",
    "CreateMutationRow",
    "CreatedMutation",
    "OutstandingInvoice",
    "OutstandingInvoicesList",
    "VatAmount",
    # Product
    "Product",
    "ProductListItem",
    "ProductList",
    "CreateProduct",
    "PatchProduct",
    "CreatedProduct",
    "ProductGroup",
    "ProductGroupList",
    # Member
    "Member",
    "MemberListItem",
    "MemberList",
    "CreateMember",
    "CreatedMember",
    # Unit
    "Unit",
    "UnitList",
]
