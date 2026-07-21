"""Filter utilities for API query parameters."""

from __future__ import annotations

import datetime
from typing import Any
from urllib.parse import quote


class Filter:
    """Base class for API filters."""

    def __init__(self, operator: str, value: Any):
        self.operator = operator
        self.value = value

    def to_param(self, field: str) -> tuple[str, str]:
        """Convert filter to query parameter tuple."""
        if self.operator == "eq":
            return (field, str(self.value))
        return (f"{field}[{self.operator}]", str(self.value))


class StringFilter(Filter):
    """Filter for string fields."""

    @classmethod
    def eq(cls, value: str) -> "StringFilter":
        """Equal to value."""
        return cls("eq", value)

    @classmethod
    def not_eq(cls, value: str) -> "StringFilter":
        """Not equal to value."""
        return cls("not_eq", value)

    @classmethod
    def like(cls, value: str) -> "StringFilter":
        """Like pattern (use % for wildcards)."""
        return cls("like", quote(value, safe=""))

    @classmethod
    def not_like(cls, value: str) -> "StringFilter":
        """Not like pattern (use % for wildcards)."""
        return cls("not_like", quote(value, safe=""))

    @classmethod
    def contains(cls, value: str) -> "StringFilter":
        """Contains value (shorthand for like %value%)."""
        return cls.like(f"%{value}%")

    @classmethod
    def starts_with(cls, value: str) -> "StringFilter":
        """Starts with value (shorthand for like value%)."""
        return cls.like(f"{value}%")

    @classmethod
    def ends_with(cls, value: str) -> "StringFilter":
        """Ends with value (shorthand for like %value)."""
        return cls.like(f"%{value}")


class IntFilter(Filter):
    """Filter for integer fields."""

    @classmethod
    def eq(cls, value: int) -> "IntFilter":
        """Equal to value."""
        return cls("eq", value)

    @classmethod
    def not_eq(cls, value: int) -> "IntFilter":
        """Not equal to value."""
        return cls("not_eq", value)

    @classmethod
    def gt(cls, value: int) -> "IntFilter":
        """Greater than value."""
        return cls("gt", value)

    @classmethod
    def gte(cls, value: int) -> "IntFilter":
        """Greater than or equal to value."""
        return cls("gte", value)

    @classmethod
    def lt(cls, value: int) -> "IntFilter":
        """Less than value."""
        return cls("lt", value)

    @classmethod
    def lte(cls, value: int) -> "IntFilter":
        """Less than or equal to value."""
        return cls("lte", value)

    @classmethod
    def between(cls, min_val: int, max_val: int) -> "IntFilter":
        """Between min and max (inclusive)."""
        return cls("range", f"{min_val},{max_val}")


class DateFilter(Filter):
    """Filter for date fields."""

    @classmethod
    def _format_date(cls, d: datetime.date | str) -> str:
        """Format date to ISO string."""
        if isinstance(d, datetime.date):
            return d.isoformat()
        return d

    @classmethod
    def eq(cls, value: datetime.date | str) -> "DateFilter":
        """Equal to date."""
        return cls("eq", cls._format_date(value))

    @classmethod
    def not_eq(cls, value: datetime.date | str) -> "DateFilter":
        """Not equal to date."""
        return cls("not_eq", cls._format_date(value))

    @classmethod
    def gt(cls, value: datetime.date | str) -> "DateFilter":
        """After date (exclusive)."""
        return cls("gt", cls._format_date(value))

    @classmethod
    def gte(cls, value: datetime.date | str) -> "DateFilter":
        """On or after date."""
        return cls("gte", cls._format_date(value))

    @classmethod
    def lt(cls, value: datetime.date | str) -> "DateFilter":
        """Before date (exclusive)."""
        return cls("lt", cls._format_date(value))

    @classmethod
    def lte(cls, value: datetime.date | str) -> "DateFilter":
        """On or before date."""
        return cls("lte", cls._format_date(value))

    @classmethod
    def between(
        cls, start: datetime.date | str, end: datetime.date | str
    ) -> "DateFilter":
        """Between dates (inclusive)."""
        return cls("range", f"{cls._format_date(start)},{cls._format_date(end)}")


def build_filter_params(filters: dict[str, Any]) -> dict[str, str]:
    """Build query parameters from a dict of filters.

    Args:
        filters: Dict where values can be raw values or Filter instances

    Returns:
        Dict of query parameter key-value pairs
    """
    params: dict[str, str] = {}
    for field, value in filters.items():
        if value is None:
            continue
        if isinstance(value, Filter):
            key, val = value.to_param(field)
            params[key] = val
        else:
            params[field] = str(value)
    return params
