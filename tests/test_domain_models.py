"""Tests for domain models."""
import pytest
from pydantic import ValidationError

from platform_core.domain.enums import (
    ColumnRole,
    IssueCode,
    PhysicalType,
    SemanticType,
    Severity,
)
from platform_core.domain.models.column import ColumnProfile, TypeCandidate
from platform_core.domain.models.dataset import Dataset
from platform_core.domain.models.profile import DatasetProfile
from platform_core.domain.models.validation import ValidationIssue


def test_type_candidate_valid() -> None:
    candidate = TypeCandidate(type="categorical", confidence=0.85, evidence=["Contains few unique strings"])
    assert candidate.type == "categorical"
    assert candidate.confidence == 0.85

def test_type_candidate_invalid() -> None:
    with pytest.raises(ValidationError):
        # confidence out of bounds
        TypeCandidate(type="numeric", confidence=1.5)

def test_column_profile_valid() -> None:
    profile = ColumnProfile(
        name="age",
        position=1,
        physical_type=PhysicalType.INTEGER,
        semantic_type=SemanticType.NUMERIC,
        role=ColumnRole.FEATURE,
        total_count=100,
        non_null_count=90,
        null_count=10,
        null_percentage=10.0,
        unique_count=50,
        unique_percentage=50.0,
        sample_values=[25, 30, 45],
        inferred_type_confidence=0.99,
        alternative_type_candidates=[
            TypeCandidate(type="categorical", confidence=0.1)
        ],
        numeric_min=18.0,
        numeric_max=85.0,
        numeric_mean=35.5,
        numeric_median=32.0,
        most_common_values=[{"value": 25, "count": 5}],
        detected_formats=["integer"]
    )
    assert profile.name == "age"
    assert profile.physical_type == PhysicalType.INTEGER

def test_column_profile_invalid() -> None:
    with pytest.raises(ValidationError):
        # Missing required field
        ColumnProfile(
            name="age",
            position=1,
            physical_type=PhysicalType.INTEGER,
            semantic_type=SemanticType.NUMERIC,
            role=ColumnRole.FEATURE,
            total_count=100,
            non_null_count=90,
            null_count=10,
            null_percentage=10.0,
            unique_count=50,
            # missing unique_percentage, inferred_type_confidence
        )

def test_validation_issue_valid() -> None:
    issue = ValidationIssue(
        code=IssueCode.HIGH_NULL_RATE,
        severity=Severity.WARNING,
        title="High missing-value rate",
        message="Column is 18% missing.",
        column_name="monthly_charges",
        affected_rows=1800,
        affected_percentage=18.0,
        evidence={"null_count": 1800, "threshold": 10.0},
        recommended_action="Impute or drop",
        auto_fix_available=False
    )
    assert issue.code == IssueCode.HIGH_NULL_RATE

def test_validation_issue_invalid() -> None:
    with pytest.raises(ValidationError):
        # Invalid enum value
        ValidationIssue(
            code="NOT_A_REAL_CODE",  # type: ignore
            severity=Severity.WARNING,
            title="Title",
            message="Msg"
        )

def test_dataset_profile_valid() -> None:
    profile = DatasetProfile(
        dataset_id="ds_123",
        file_name="data.csv",
        file_format="csv",
        created_at="2026-07-28T14:30:00Z",
        row_count=100,
        column_count=2,
        duplicate_row_count=0,
        memory_usage_bytes=1024,
        columns=[],
        validation_issues=[],
        quality_score=95.5,
        summary={"status": "good"}
    )
    assert profile.dataset_id == "ds_123"

def test_dataset_profile_invalid() -> None:
    with pytest.raises(ValidationError):
        # Invalid type for row_count
        DatasetProfile(
            dataset_id="ds_123",
            file_name="data.csv",
            file_format="csv",
            created_at="2026-07-28T14:30:00Z",
            row_count="many",  # type: ignore
            column_count=2,
            duplicate_row_count=0,
            memory_usage_bytes=1024,
            columns=[],
            validation_issues=[],
            quality_score=95.5,
            summary={}
        )

def test_dataset_valid() -> None:
    ds = Dataset(
        dataset_id="ds_123",
        file_name="data.csv",
        file_format="csv",
        staged_dataset_path="/tmp/ds_123.parquet"
    )
    assert ds.dataset_id == "ds_123"

def test_dataset_invalid() -> None:
    with pytest.raises(ValidationError):
        Dataset(
            dataset_id="ds_123",
            # missing file_name and file_format
        )
