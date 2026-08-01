"""Validation rules implementations."""
import polars as pl

from platform_core.domain.enums import IssueCode, Severity
from platform_core.domain.models.validation import ValidationIssue
from platform_core.validation.base import ValidationRule


class HighNullRateRule(ValidationRule):
    def __init__(self, threshold: float = 0.10):
        self.threshold = threshold

    def evaluate(self, df: pl.DataFrame) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        total_rows = df.height
        if total_rows == 0:
            return issues

        for col in df.columns:
            null_count = df[col].null_count()
            null_percentage = null_count / total_rows

            if null_percentage > self.threshold:
                issues.append(
                    ValidationIssue(
                        code=IssueCode.HIGH_NULL_RATE,
                        severity=Severity.WARNING,
                        title=f"High null rate in column '{col}'",
                        message=f"Column '{col}' has {null_percentage:.1%} null values, exceeding the {self.threshold:.1%} threshold.",
                        column_name=col,
                        affected_rows=null_count,
                        affected_percentage=null_percentage * 100,
                        evidence={"null_count": null_count, "null_percentage": null_percentage, "threshold": self.threshold},
                        recommended_action="Consider imputing missing values or dropping the column.",
                        auto_fix_available=False,
                    )
                )
        return issues


class DuplicateRowsRule(ValidationRule):
    def __init__(self, exact_duplicate_count: int | None = None):
        self.exact_duplicate_count = exact_duplicate_count

    def evaluate(self, df: pl.DataFrame) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        total_rows = df.height
        if total_rows == 0:
            return issues

        if self.exact_duplicate_count is not None:
            duplicate_count = self.exact_duplicate_count
        else:
            unique_rows = df.unique().height
            duplicate_count = total_rows - unique_rows
        
        if duplicate_count > 0:
            issues.append(
                ValidationIssue(
                    code=IssueCode.DUPLICATE_ROWS,
                    severity=Severity.WARNING,
                    title="Duplicate rows detected",
                    message=f"Dataset contains {duplicate_count} duplicate rows.",
                    column_name=None,
                    affected_rows=duplicate_count,
                    affected_percentage=(duplicate_count / total_rows) * 100,
                    evidence={"duplicate_count": duplicate_count, "total_rows": total_rows},
                    recommended_action="Deduplicate the dataset to prevent data leakage or skewed metrics.",
                    auto_fix_available=False,
                )
            )
        return issues


class ConstantColumnRule(ValidationRule):
    def evaluate(self, df: pl.DataFrame) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        total_rows = df.height
        if total_rows == 0:
            return issues

        for col in df.columns:
            n_unique = df[col].n_unique()
            if n_unique <= 1:
                issues.append(
                    ValidationIssue(
                        code=IssueCode.CONSTANT_COLUMN,
                        severity=Severity.WARNING,
                        title=f"Constant column '{col}'",
                        message=f"Column '{col}' has only {n_unique} unique value(s) and provides no variance.",
                        column_name=col,
                        affected_rows=total_rows,
                        affected_percentage=100.0,
                        evidence={"n_unique": n_unique},
                        recommended_action="Drop the constant column as it provides no useful information.",
                        auto_fix_available=False,
                    )
                )
        return issues


class MixedTypeRule(ValidationRule):
    def evaluate(self, df: pl.DataFrame) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        total_rows = df.height
        if total_rows == 0:
            return issues

        for col in df.columns:
            dtype = df[col].dtype
            if dtype in (pl.String, pl.Utf8):
                s_not_null = df[col].drop_nulls()
                non_null_count = s_not_null.len()
                if non_null_count == 0:
                    continue
                
                parsed_as_float = s_not_null.cast(pl.Float64, strict=False).drop_nulls().len()
                
                if 0 < parsed_as_float < non_null_count:
                    issues.append(
                        ValidationIssue(
                            code=IssueCode.MIXED_TYPE,
                            severity=Severity.ERROR,
                            title=f"Mixed types in column '{col}'",
                            message=f"Column '{col}' contains both numeric ({parsed_as_float}) and non-numeric ({non_null_count - parsed_as_float}) values.",
                            column_name=col,
                            affected_rows=non_null_count,
                            affected_percentage=(non_null_count / total_rows) * 100,
                            evidence={"numeric_count": parsed_as_float, "string_count": non_null_count - parsed_as_float},
                            recommended_action="Standardize column values to a single type or split the column.",
                            auto_fix_available=False,
                        )
                    )
        return issues
