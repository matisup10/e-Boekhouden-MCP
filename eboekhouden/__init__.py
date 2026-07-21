"""Bundled e-Boekhouden API client used by the MCP server.

This package is implementation support for ``eboekhouden_mcp`` so the MCP
distribution can be installed standalone.

Example usage:
    from eboekhouden import EBoekhoudenClient
    from eboekhouden.models import CreateInvoice, CreateInvoiceItem
    from eboekhouden.models.enums import VatCode

    with EBoekhoudenClient() as client:
        # List relations
        relations = client.relations.list()

        # Create an invoice
        invoice = CreateInvoice(
            relation_id=123,
            term_of_payment=30,
            template_id=1,
            items=[CreateInvoiceItem(
                description="Services",
                quantity=1,
                price_per_unit=100.00,
                vat_code=VatCode.HOOG_VERK_21,
                ledger_id=8000,
            )]
        )
        result = client.invoices.create(invoice)
"""

from eboekhouden.client import EBoekhoudenClient
from eboekhouden.config import EBoekhoudenConfig
from eboekhouden.exceptions import (
    APIError,
    AuthenticationError,
    EBoekhoudenError,
    NotFoundError,
    RateLimitError,
    SecurityError,
    SessionExpiredError,
    ValidationError,
)
from eboekhouden.filters import DateFilter, Filter, IntFilter, StringFilter

__version__ = "0.2.0"

__all__ = [
    # Client
    "EBoekhoudenClient",
    "EBoekhoudenConfig",
    # Exceptions
    "EBoekhoudenError",
    "APIError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "SecurityError",
    "SessionExpiredError",
    "ValidationError",
    # Filters
    "Filter",
    "StringFilter",
    "IntFilter",
    "DateFilter",
]
