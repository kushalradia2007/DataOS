"""Profile models."""
from typing import Any, Literal

from pydantic import BaseModel

from platform_core.domain.models.column import ColumnProfile
from platform_core.domain.models.validation import ValidationIssue


class DatasetProfile(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    dataset_id: str
    file_name: str
    file_format: str
    created_at: str

    row_count: int
    column_count: int
    duplicate_row_count: int
    memory_usage_bytes: int

    columns: list[ColumnProfile]
    validation_issues: list[ValidationIssue]

    quality_score: float
    summary: dict[str, Any]
