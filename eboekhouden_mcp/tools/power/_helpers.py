"""Shared helpers for the power tools.

Pure functions plus one thin hydration helper that takes a getter callable.
Kept dependency-light so each tool stays a small, focused adapter.
"""

from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any, Callable, Iterable

from eboekhouden.filters import DateFilter, IntFilter


def compact(obj: Any, drop_empty: bool = True) -> Any:
    """Recursively drop ``None`` and empty ``str``/``list``/``dict`` from dicts.

    ``0``, ``False`` and ``Decimal(0)`` are preserved — only genuinely empty
    values are removed. When ``drop_empty`` is ``False`` the object is returned
    unchanged (the ``verbose`` escape hatch).
    """
    if not drop_empty:
        return obj
    if isinstance(obj, dict):
        result: dict[Any, Any] = {}
        for key, value in obj.items():
            cleaned = compact(value, drop_empty)
            if _is_empty(cleaned):
                continue
            result[key] = cleaned
        return result
    if isinstance(obj, (list, tuple)):
        return [compact(value, drop_empty) for value in obj]
    return obj


def _is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value == "":
        return True
    if isinstance(value, (list, tuple, dict)) and len(value) == 0:
        return True
    return False


def hydrate(
    getter: Callable[[int], Any],
    ids: Iterable[int],
    cap: int,
) -> tuple[list[dict[str, Any]], bool, int]:
    """Fetch detail for up to ``cap`` ids via ``getter``.

    Sequential on purpose: the SDK client shares one auto-refreshing session,
    so parallel ``get()`` calls risk racing the token refresh. The cap bounds
    latency and token cost.

    Returns ``(items, truncated, total)`` where ``items`` are ``model_dump()``
    dicts, ``truncated`` is ``True`` when more than ``cap`` ids were supplied,
    and ``total`` is the number of ids requested.
    """
    id_list = list(ids)
    total = len(id_list)
    truncated = total > cap
    selected = id_list[:cap]
    items: list[dict[str, Any]] = []
    for identifier in selected:
        obj = getter(identifier)
        items.append(obj.model_dump() if hasattr(obj, "model_dump") else obj)
    return items, truncated, total


def apply_filters(
    items: list[Any],
    predicates: dict[str, Callable[[Any], bool]],
) -> list[Any]:
    """Keep items for which every predicate returns truthy (logical AND).

    The predicate keys are descriptive only; they make call sites readable.
    """
    result = items
    for predicate in predicates.values():
        result = [item for item in result if predicate(item)]
    return result


def range_date_filter(
    date_from: datetime.date | str | None,
    date_to: datetime.date | str | None,
) -> DateFilter | None:
    """Build a server-side date filter from an optional open/closed range."""
    if date_from is not None and date_to is not None:
        return DateFilter.between(date_from, date_to)
    if date_from is not None:
        return DateFilter.gte(date_from)
    if date_to is not None:
        return DateFilter.lte(date_to)
    return None


def range_int_filter(low: int | None, high: int | None) -> IntFilter | None:
    """Build a server-side integer filter from an optional open/closed range."""
    if low is not None and high is not None:
        return IntFilter.between(low, high)
    if low is not None:
        return IntFilter.gte(low)
    if high is not None:
        return IntFilter.lte(high)
    return None


def parse_date(value: datetime.date | str | None) -> datetime.date | None:
    """Coerce an ISO date string (or date) to a ``datetime.date``; pass None through."""
    if value is None:
        return None
    if isinstance(value, datetime.date):
        return value
    return datetime.date.fromisoformat(str(value)[:10])


def to_float(value: Any) -> float | None:
    """Coerce Decimal/str/number to float; pass through None."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def round2(value: Any) -> float:
    """Round a money value to 2 decimals as a float."""
    return round(float(value), 2)


def to_markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    """Render rows as a GitHub-flavoured markdown table.

    Floats are formatted to 2 decimals; missing cells render empty.
    Returns an empty string for no rows.
    """
    if not rows:
        return ""
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    lines = [header, separator]
    for row in rows:
        cells = [_fmt_cell(row.get(column, "")) for column in columns]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _fmt_cell(value: Any) -> str:
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return f"{value:.2f}"
    if isinstance(value, Decimal):
        return f"{float(value):.2f}"
    return str(value)


def capped_result(
    items: list[Any],
    truncated: bool,
    total_matches: int,
    *,
    hint: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble the standard capped/compact result envelope."""
    result: dict[str, Any] = {
        "count": len(items),
        "total_matches": total_matches,
        "truncated": truncated,
        "items": items,
    }
    if truncated and hint:
        result["hint"] = hint
    if extra:
        result.update(extra)
    return result
