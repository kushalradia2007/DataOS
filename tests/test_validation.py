"""Tests for validation rules."""
import polars as pl

from platform_core.domain.enums import IssueCode
from platform_core.validation.rules import (
    ConstantColumnRule,
    DuplicateRowsRule,
    HighNullRateRule,
    MixedTypeRule,
)


def test_high_null_rate_positive():
    rule = HighNullRateRule(threshold=0.10)
    # 2 nulls out of 10 = 20% > 10%
    df = pl.DataFrame({"a": [1, 2, 3, 4, 5, 6, 7, 8, None, None]})
    issues = rule.evaluate(df)
    assert len(issues) == 1
    assert issues[0].code == IssueCode.HIGH_NULL_RATE
    assert issues[0].column_name == "a"


def test_high_null_rate_negative():
    rule = HighNullRateRule(threshold=0.10)
    # 1 null out of 10 = 10% not > 10%
    df = pl.DataFrame({"a": [1, 2, 3, 4, 5, 6, 7, 8, 9, None]})
    issues = rule.evaluate(df)
    assert len(issues) == 0


def test_duplicate_rows_positive():
    rule = DuplicateRowsRule()
    df = pl.DataFrame({"a": [1, 2, 2, 3], "b": ["x", "y", "y", "z"]})
    issues = rule.evaluate(df)
    assert len(issues) == 1
    assert issues[0].code == IssueCode.DUPLICATE_ROWS
    assert issues[0].affected_rows == 1


def test_duplicate_rows_negative():
    rule = DuplicateRowsRule()
    df = pl.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    issues = rule.evaluate(df)
    assert len(issues) == 0


def test_constant_column_positive():
    rule = ConstantColumnRule()
    df = pl.DataFrame({"a": [5, 5, 5], "b": [1, 2, 3]})
    issues = rule.evaluate(df)
    assert len(issues) == 1
    assert issues[0].code == IssueCode.CONSTANT_COLUMN
    assert issues[0].column_name == "a"


def test_constant_column_negative():
    rule = ConstantColumnRule()
    df = pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    issues = rule.evaluate(df)
    assert len(issues) == 0


def test_mixed_type_positive():
    rule = MixedTypeRule()
    df = pl.DataFrame({"a": ["1", "2.5", "foo", "bar"]})
    issues = rule.evaluate(df)
    assert len(issues) == 1
    assert issues[0].code == IssueCode.MIXED_TYPE
    assert issues[0].column_name == "a"


def test_mixed_type_negative():
    rule = MixedTypeRule()
    # "a" is pure text, "b" is pure numeric string (which gets cast to float)
    df = pl.DataFrame({"a": ["foo", "bar", "baz"], "b": ["1", "2.5", "3"]})
    issues = rule.evaluate(df)
    assert len(issues) == 0
