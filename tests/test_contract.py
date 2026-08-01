"""Contract compliance tests."""
from platform_core.domain.enums import IssueCode, SemanticType
from platform_core.domain.models.profile import DatasetProfile


def test_semantic_type_enum_contract() -> None:
    expected = {
        "numeric", "categorical", "datetime", "text", 
        "identifier", "boolean", "unknown"
    }
    actual = {e.value for e in SemanticType}
    assert actual == expected

def test_issue_code_enum_contract() -> None:
    expected = {
        "high_null_rate", "duplicate_rows", 
        "constant_column", "mixed_type"
    }
    actual = {e.value for e in IssueCode}
    assert actual == expected

def test_dataset_profile_schema_version() -> None:
    profile = DatasetProfile(
        dataset_id="ds_12345678",
        file_name="test.csv",
        file_format="csv",
        created_at="2023-01-01T00:00:00Z",
        row_count=10,
        column_count=2,
        duplicate_row_count=0,
        memory_usage_bytes=100,
        columns=[],
        validation_issues=[],
        quality_score=100.0,
        summary={}
    )
    assert profile.schema_version == "1.0"
    dump = profile.model_dump(mode="json")
    assert dump["schema_version"] == "1.0"
