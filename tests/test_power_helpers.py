"""Tests for the power-tools shared helpers."""

from __future__ import annotations

from decimal import Decimal

from eboekhouden.filters import DateFilter, IntFilter
from eboekhouden_mcp.tools.power._helpers import (
    apply_filters,
    compact,
    hydrate,
    range_date_filter,
    range_int_filter,
    round2,
    to_markdown_table,
)


class TestCompact:
    def test_drops_none_and_empty_but_keeps_zero_and_false(self):
        result = compact(
            {"a": None, "b": 0, "c": "", "d": "x", "e": [], "f": {}, "g": False}
        )
        assert result == {"b": 0, "d": "x", "g": False}

    def test_recurses_into_nested_dicts(self):
        result = compact({"outer": {"keep": 1, "drop": None}})
        assert result == {"outer": {"keep": 1}}

    def test_recurses_into_lists_of_dicts(self):
        result = compact({"rows": [{"x": None, "y": 2}, {"z": 3}]})
        assert result == {"rows": [{"y": 2}, {"z": 3}]}

    def test_verbose_mode_keeps_everything(self):
        payload = {"a": None, "b": ""}
        assert compact(payload, drop_empty=False) == payload


class _Fake:
    def __init__(self, id: int) -> None:
        self.id = id

    def model_dump(self) -> dict:
        return {"id": self.id, "name": f"n{self.id}"}


class TestHydrate:
    def test_fetches_each_id_and_returns_dumps(self):
        items, truncated, total = hydrate(_Fake, [1, 2, 3], cap=10)
        assert truncated is False
        assert total == 3
        assert items == [
            {"id": 1, "name": "n1"},
            {"id": 2, "name": "n2"},
            {"id": 3, "name": "n3"},
        ]

    def test_respects_cap_and_flags_truncation(self):
        calls: list[int] = []

        def getter(i: int) -> _Fake:
            calls.append(i)
            return _Fake(i)

        items, truncated, total = hydrate(getter, [1, 2, 3, 4, 5], cap=2)
        assert len(items) == 2
        assert truncated is True
        assert total == 5
        # Cap must prevent extra fetches (token / latency guard).
        assert calls == [1, 2]


class TestApplyFilters:
    def test_composes_predicates_with_and(self):
        items = [{"a": 1, "b": 5}, {"a": 1, "b": 9}, {"a": 2, "b": 5}]
        result = apply_filters(
            items,
            {
                "a_is_1": lambda it: it["a"] == 1,
                "b_is_5": lambda it: it["b"] == 5,
            },
        )
        assert result == [{"a": 1, "b": 5}]

    def test_no_predicates_returns_all(self):
        items = [{"a": 1}]
        assert apply_filters(items, {}) == items


class TestRangeFilters:
    def test_date_range_both_sides(self):
        f = range_date_filter("2026-01-01", "2026-12-31")
        assert isinstance(f, DateFilter)
        assert f.to_param("date") == ("date[range]", "2026-01-01,2026-12-31")

    def test_date_range_single_side(self):
        assert range_date_filter("2026-01-01", None).operator == "gte"
        assert range_date_filter(None, "2026-12-31").operator == "lte"
        assert range_date_filter(None, None) is None

    def test_int_range(self):
        assert isinstance(range_int_filter(1, 9), IntFilter)
        assert range_int_filter(5, None).operator == "gte"
        assert range_int_filter(None, 5).operator == "lte"
        assert range_int_filter(None, None) is None


class TestFormatting:
    def test_round2_handles_decimal(self):
        assert round2(Decimal("1.005")) == 1.0 or round2(Decimal("1.006")) == 1.01
        assert round2(Decimal("12.3456")) == 12.35

    def test_markdown_table(self):
        rows = [{"code": "8000", "balance": 1234.5}, {"code": "4000", "balance": -10.0}]
        table = to_markdown_table(rows, ["code", "balance"])
        lines = table.splitlines()
        assert lines[0] == "| code | balance |"
        assert lines[1] == "| --- | --- |"
        assert lines[2] == "| 8000 | 1234.50 |"
        assert lines[3] == "| 4000 | -10.00 |"

    def test_markdown_table_empty(self):
        assert to_markdown_table([], ["a"]) == ""
