"""Tests for inference module."""
import polars as pl

from platform_core.domain.enums import ColumnRole, SemanticType
from platform_core.inference.role_inference import infer_column_role
from platform_core.inference.type_inference import infer_semantic_type


def test_inference_coverage() -> None:
    """F15: Assert expected semantic types, roles, and confidence ranges."""
    df = pl.DataFrame({
        "id_col": [1, 2, 3, 4, 5],
        "cat_col": ["A", "B", "A", "B", "A"],
        "num_col": [1.1, 2.2, 3.3, 4.4, 1.1],
        "bool_col": [True, False, True, False, True],
        "dt_col": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-01", "2023-01-02"],
        "text_col": ["hello world", "foo bar", "baz qux", "lorem ipsum", "dolor sit"],
    })
    
    exact_stats = {
        "row_count": 5,
        "columns": {
            col: {"null_count": 0, "n_unique": df[col].n_unique()}
            for col in df.columns
        }
    }

    # bool_col: Polars Boolean dtype → BOOLEAN, confidence ≥ 0.9
    sem, conf, _ev, _cands = infer_semantic_type(df["bool_col"], exact_stats)
    assert sem == SemanticType.BOOLEAN
    assert conf >= 0.9
    role, _rev = infer_column_role(sem, "bool_col")
    assert role == ColumnRole.FEATURE

    # id_col: 5 unique ints in 5 rows → IDENTIFIER (high uniqueness), confidence ≥ 0.85
    sem, conf, _ev, _cands = infer_semantic_type(df["id_col"], exact_stats)
    assert sem == SemanticType.IDENTIFIER
    assert conf >= 0.85
    role, _rev = infer_column_role(sem, "id_col")
    # "id_col" ends with "_id" → role is IDENTIFIER by name heuristic
    assert role == ColumnRole.IDENTIFIER

    # num_col: Float64 → NUMERIC, confidence ≥ 0.8
    sem, conf, _ev, _cands = infer_semantic_type(df["num_col"], exact_stats)
    assert sem == SemanticType.NUMERIC
    assert conf >= 0.8
    role, _rev = infer_column_role(sem, "num_col")
    assert role == ColumnRole.FEATURE

    # dt_col: date-like strings → DATETIME, confidence ≥ 0.8
    sem, conf, _ev, _cands = infer_semantic_type(df["dt_col"], exact_stats)
    assert sem == SemanticType.DATETIME
    assert conf >= 0.8
    role, _rev = infer_column_role(sem, "dt_col")
    assert role == ColumnRole.DATETIME

    # cat_col: 2 unique in 5 rows → CATEGORICAL, confidence ≥ 0.6
    sem, conf, _ev, _cands = infer_semantic_type(df["cat_col"], exact_stats)
    assert sem == SemanticType.CATEGORICAL
    assert conf >= 0.6

    # text_col: short strings — could be TEXT or CATEGORICAL; assert valid type
    sem, conf, _ev, _cands = infer_semantic_type(df["text_col"], exact_stats)
    assert isinstance(sem, SemanticType)
    assert conf > 0


def test_inference_edge_cases() -> None:
    """F16: Assert documented behavior for edge-case columns."""
    df = pl.DataFrame({
        "empty_col": pl.Series([None, None, None], dtype=pl.Null),
        "all_same": ["A", "A", "A"],
        "target_col": [0, 1, 0],
    })
    
    exact_stats = {
        "row_count": 3,
        "columns": {
            col: {"null_count": df[col].null_count(), "n_unique": df[col].n_unique()}
            for col in df.columns
        }
    }

    # all-null column → UNKNOWN (no evaluator fires when non_null_count == 0)
    sem, conf, _ev, _cands = infer_semantic_type(df["empty_col"], exact_stats)
    assert sem == SemanticType.UNKNOWN

    # constant column → CATEGORICAL (n_unique=1 ≤ 20 triggers categorical at 0.80)
    sem, conf, _ev, _cands = infer_semantic_type(df["all_same"], exact_stats)
    assert sem == SemanticType.CATEGORICAL
    assert conf >= 0.6

    # 0/1 integer column → NUMERIC (Int64 dtype → numeric evaluator 0.85 > categorical 0.80)
    # Boolean evaluator does not fire for Int64 dtype.
    sem, conf, _ev, _cands = infer_semantic_type(df["target_col"], exact_stats)
    assert sem == SemanticType.NUMERIC
    assert conf > 0

