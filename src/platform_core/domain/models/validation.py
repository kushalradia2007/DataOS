"""Validation models."""
from typing import Any

from pydantic import BaseModel, Field

from platform_core.domain.enums import IssueCode, Severity


class ValidationIssue(BaseModel):
    code: IssueCode
    severity: Severity
    title: str
    message: str

    column_name: str | None = None
    affected_rows: int | None = None
    affected_percentage: float | None = None

    evidence: dict[str, Any] = Field(default_factory=dict)
    recommended_action: str | None = None
    auto_fix_available: bool = False
