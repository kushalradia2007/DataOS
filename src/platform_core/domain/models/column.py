"""Column models."""
from pydantic import BaseModel, Field

from platform_core.domain.enums import ColumnRole, PhysicalType, SemanticType


class TypeCandidate(BaseModel):
    type: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)

class ColumnProfile(BaseModel):
    name: str
    position: int
    physical_type: PhysicalType
    semantic_type: SemanticType
    role: ColumnRole

    total_count: int
    non_null_count: int
    null_count: int
    null_percentage: float

    unique_count: int
    unique_percentage: float
    sample_values: list[str | int | float | bool | None] = Field(default_factory=list)

    inferred_type_confidence: float
    alternative_type_candidates: list[TypeCandidate] = Field(default_factory=list)

    numeric_min: float | None = None
    numeric_max: float | None = None
    numeric_mean: float | None = None
    numeric_median: float | None = None

    # Changed from list[dict] to list[dict[str, int]] or similar, but for now list[dict[str, int]] might be safer for mypy
    # or just list[dict[str, str | int]]
    most_common_values: list[dict[str, str | int | float]] = Field(default_factory=list)
    detected_formats: list[str] = Field(default_factory=list)
