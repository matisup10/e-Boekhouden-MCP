"""Enums for the e-Boekhouden SDK."""

from enum import Enum


class VatCode(str, Enum):
    """VAT codes for the Netherlands and Belgium."""

    # Netherlands - Sales
    HOOG_VERK_21 = "HOOG_VERK_21"  # 21% VAT sale
    LAAG_VERK_9 = "LAAG_VERK_9"  # 9% VAT sale
    LAAG_VERK = "LAAG_VERK"  # 6% VAT sale (before 2019-01-01)
    VERL_VERK = "VERL_VERK"  # Reverse charge 21% sale
    VERL_VERK_L9 = "VERL_VERK_L9"  # Reverse charge 9% sale
    AFW_VERK = "AFW_VERK"  # Divergent sale
    BU_EU_VERK = "BU_EU_VERK"  # Delivery outside EU 0%
    BI_EU_VERK = "BI_EU_VERK"  # Delivery within EU 0%
    BI_EU_VERK_D = "BI_EU_VERK_D"  # Services within EU 0%
    AFST_VERK = "AFST_VERK"  # Distance selling within EU 0%

    # Netherlands - Purchases
    HOOG_INK_21 = "HOOG_INK_21"  # 21% VAT purchase
    LAAG_INK_9 = "LAAG_INK_9"  # 9% VAT purchase
    LAAG_INK = "LAAG_INK"  # 6% VAT purchase (before 2019-01-01)
    VERL_INK = "VERL_INK"  # Reverse charge 21% purchase
    VERL_INK_L9 = "VERL_INK_L9"  # Reverse charge 9% purchase
    VERL_INK_L = "VERL_INK_L"  # Reverse charge 6% purchase (before 2019-01-01)
    AFW = "AFW"  # Divergent purchase
    BU_EU_INK = "BU_EU_INK"  # Delivery/services outside EU 0%
    BI_EU_INK = "BI_EU_INK"  # Delivery/services within EU 0%

    # General
    GEEN = "GEEN"  # No VAT

    # Belgium - Sales
    BE_0_VERK = "BE_0_VERK"  # Domestic sale 0%
    BE_6_VERK = "BE_6_VERK"  # Domestic sale 6%
    BE_12_VERK = "BE_12_VERK"  # Domestic sale 12%
    BE_21_VERK = "BE_21_VERK"  # Domestic sale 21%
    BE_IC_D_VERK = "BE_IC_D_VERK"  # Intra-comm. service EU 0%
    BE_VERL_VERK = "BE_VERL_VERK"  # Reverse charge co-contractor 0%
    BE_IC_VERK = "BE_IC_VERK"  # Intra-comm. goods EU 0%
    BE_EXP_VERK = "BE_EXP_VERK"  # Export sale 0%

    # Belgium - Purchases
    BE_0_INK = "BE_0_INK"  # Domestic purchase 0%
    BE_6_INK = "BE_6_INK"  # Domestic purchase 6%
    BE_12_INK = "BE_12_INK"  # Domestic purchase 12%
    BE_21_INK = "BE_21_INK"  # Domestic purchase 21%
    BE_VERL_0_INK = "BE_VERL_0_INK"  # Reverse charge co-contractor 0%
    BE_VERL_6_INK = "BE_VERL_6_INK"  # Reverse charge co-contractor 6%
    BE_VERL_12_INK = "BE_VERL_12_INK"  # Reverse charge co-contractor 12%
    BE_VERL_21_INK = "BE_VERL_21_INK"  # Reverse charge co-contractor 21%
    BE_IC_D_0_INK = "BE_IC_D_0_INK"  # Intra-comm. service EU 0%
    BE_IC_D_6_INK = "BE_IC_D_6_INK"  # Intra-comm. service EU 6%
    BE_IC_D_12_INK = "BE_IC_D_12_INK"  # Intra-comm. service EU 12%
    BE_IC_D_21_INK = "BE_IC_D_21_INK"  # Intra-comm. service EU 21%
    BE_IC_0_INK = "BE_IC_0_INK"  # Intra-comm. goods EU 0%
    BE_IC_6_INK = "BE_IC_6_INK"  # Intra-comm. goods EU 6%
    BE_IC_12_INK = "BE_IC_12_INK"  # Intra-comm. goods EU 12%
    BE_IC_21_INK = "BE_IC_21_INK"  # Intra-comm. goods EU 21%
    BE_IMP_0_INK = "BE_IMP_0_INK"  # Import reverse charge 0%
    BE_IMP_6_INK = "BE_IMP_6_INK"  # Import reverse charge 6%
    BE_IMP_12_INK = "BE_IMP_12_INK"  # Import reverse charge 12%
    BE_IMP_21_INK = "BE_IMP_21_INK"  # Import reverse charge 21%


class MutationType(str, Enum):
    """Types of mutations/journal entries."""

    INVOICE_RECEIVED = "1"  # Inkoopfactuur
    INVOICE_SENT = "2"  # Verkoopfactuur
    PAYMENT_RECEIVED = "3"  # Ontvangen factuur betaling
    PAYMENT_SENT = "4"  # Verstuurde factuur betaling
    MONEY_RECEIVED = "5"  # Geld ontvangen
    MONEY_SENT = "6"  # Geld uitgegeven
    GENERAL_JOURNAL = "7"  # Memoriaal


class RelationType(str, Enum):
    """Types of relations."""

    BUSINESS = "B"  # Bedrijf
    PRIVATE = "P"  # Particulier


class Gender(str, Enum):
    """Gender options."""

    MALE = "m"
    FEMALE = "v"
    DEPARTMENT = "a"


class InExVat(str, Enum):
    """Indicates if amounts include or exclude VAT."""

    INCLUSIVE = "IN"
    EXCLUSIVE = "EX"


class MandateType(str, Enum):
    """Types of direct debit mandates."""

    ONE_TIME = "E"  # Eenmalig
    RECURRING = "D"  # Doorlopend


class LedgerCategory(str, Enum):
    """Ledger account categories."""

    BALANCE = "BAL"  # Balans
    PROFIT_LOSS = "VW"  # Verlies en winst
    VAT_LOW = "AF6"  # Omzetbelasting laag tarief
    VAT_HIGH = "AF19"  # Omzetbelasting hoog tarief
    VAT_OTHER = "AFOVERIG"  # Omzetbelasting overig
    INPUT_TAX = "VOOR"  # Voorbelasting
    VAT_CURRENT = "BTWRC"  # BTW rekening-courant
    LIQUID_ASSETS = "FIN"  # Liquide middelen
    DEBTORS = "DEB"  # Debiteuren
    CREDITORS = "CRED"  # Crediteuren
    VAT = "AF"  # Omzetbelasting
