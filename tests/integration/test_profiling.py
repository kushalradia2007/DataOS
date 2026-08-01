"""Integration tests for profiling service."""
import json
from pathlib import Path
from unittest.mock import patch

import polars as pl
import pytest

from platform_core.profiling.service import ProfilingService

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

@pytest.fixture
def expected_stats() -> dict[str, dict[str, dict]]:
    stats_file = FIXTURES_DIR / "expected_stats.json"
    with open(stats_file) as f:
        return json.load(f)

def test_profiling_dirty_sales(expected_stats: dict[str, dict[str, dict]]) -> None:
    # dirty_sales contains a duplicate row and a missing value
    df = pl.read_csv(FIXTURES_DIR / "dirty_sales.csv")
    
    service = ProfilingService()
    profile = service.profile(df, "ds_dirty123")
    
    expected = expected_stats["dirty_sales"]
    
    assert profile.row_count == expected["row_count"]
    assert profile.duplicate_row_count == expected["duplicate_rows"]
    
    for col_profile in profile.columns:
        col_name = col_profile.name
        assert col_profile.null_count == expected["null_counts"][col_name]
        assert col_profile.unique_count == expected["n_unique"][col_name]
        
    # Check that HTML report was saved
    assert profile.summary["html_report_path"] is not None
    assert Path(profile.summary["html_report_path"]).exists()

def test_profiling_fallback() -> None:
    df = pl.read_csv(FIXTURES_DIR / "mixed_types.csv")
    
    service = ProfilingService()
    
    # Mock mapper to raise Exception
    with patch("platform_core.profiling.service.run_and_map_profile", side_effect=Exception("Library crash")):
        profile = service.profile(df, "ds_fallback123")
        
    assert profile.summary.get("fallback_used") is True
    assert profile.row_count == 3
    # Check null counts
    
    col_dict = {c.name: c for c in profile.columns}
    assert col_dict["a"].null_count == 0
    assert col_dict["c"].null_count == 1

def test_profiling_sampling(monkeypatch: pytest.MonkeyPatch) -> None:
    # We will just patch df.height to trigger sampling branch
    _df = pl.read_csv(FIXTURES_DIR / "dirty_sales.csv")
    
    # Actually df.height is a property, monkeypatching it on the instance is hard in polars
    # Let's create a DataFrame with 10001 rows
    df_large = pl.DataFrame({
        "id": range(10001),
        "val": ["A"] * 10001
    })
    
    service = ProfilingService()
    profile = service.profile(df_large, "ds_large123")
    
    assert profile.summary.get("sampling_applied") is True
    assert profile.summary.get("sample_size") == 10000
    
    # Row count should still be exact full size!
    assert profile.row_count == 10001

def test_imports_isolation() -> None:
    """rglob src/ to assert that data_profiling is ONLY imported in mapper.py."""
    src_dir = Path(__file__).parent.parent.parent / "src"
    
    files_with_import = []
    for py_file in src_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            if "data_profiling" in content:
                files_with_import.append(str(py_file))
        except OSError:
            continue
            
    for f in files_with_import:
        assert f.endswith(("mapper.py", "mapper.py".replace("/", "\\"))), f"data_profiling imported outside mapper.py: {f}"

def test_profiling_percentages() -> None:
    """Regression test for Finding 1: null_percentage and unique_percentage units."""
    # 15 nulls in 100 rows
    df = pl.DataFrame({
        "a": [None] * 15 + [1] * 85,
        "b": list(range(100)) # 100 unique values
    })
    
    service = ProfilingService()
    profile = service.profile(df, "ds_perc123")
    
    cols = {c.name: c for c in profile.columns}
    assert cols["a"].null_percentage == 15.0
    assert cols["a"].unique_percentage == 2.0  # 1 unique value + null if counted, or 1 depending on n_unique
    
    assert cols["b"].unique_percentage == 100.0
    assert cols["b"].null_percentage == 0.0

def test_profiling_single_row_percentages() -> None:
    """one unique value in one row => unique_percentage == 100.0"""
    df = pl.DataFrame({"a": [42]})
    service = ProfilingService()
    profile = service.profile(df, "ds_single123")
    
    cols = {c.name: c for c in profile.columns}
    assert cols["a"].unique_percentage == 100.0
    assert cols["a"].null_percentage == 0.0

def test_profiling_zero_rows() -> None:
    """zero-row behavior is explicit and tested."""
    df = pl.DataFrame({"a": [], "b": []}, schema={"a": pl.Int64, "b": pl.String})
    service = ProfilingService()
    profile = service.profile(df, "ds_zero123")
    
    cols = {c.name: c for c in profile.columns}
    assert cols["a"].null_percentage == 0.0
    assert cols["a"].unique_percentage == 0.0
    assert cols["b"].null_percentage == 0.0
    assert cols["b"].unique_percentage == 0.0

def test_profiling_sampling_max_override() -> None:
    # 50001 rows with one 999999 outlier
    df = pl.DataFrame({
        "id": range(50001),
        "price": [10.0] * 50000 + [999999.0]
    })
    
    service = ProfilingService()
    profile = service.profile(df, "ds_max1234")
    
    cols = {c.name: c for c in profile.columns}
    assert cols["price"].numeric_max == 999999.0
    
    # Check fallback as well
    with patch("platform_core.profiling.service.run_and_map_profile", side_effect=Exception("Crash")):
        fallback_profile_result = service.profile(df, "ds_max_f1234")
        fallback_cols = {c.name: c for c in fallback_profile_result.columns}
        assert fallback_cols["price"].numeric_max == 999999.0


def test_profiling_all_null_numeric_fallback() -> None:
    """F17/F14 regression: all-null numeric column must emit None, not 0.0, in fallback path."""
    df = pl.DataFrame({"x": pl.Series([None, None, None], dtype=pl.Float64)})

    service = ProfilingService()

    with patch("platform_core.profiling.service.run_and_map_profile", side_effect=Exception("Crash")):
        profile = service.profile(df, "ds_nullfb01")

    assert profile.summary.get("fallback_used") is True
    cols = {c.name: c for c in profile.columns}
    x = cols["x"]
    assert x.numeric_min is None, f"Expected None, got {x.numeric_min}"
    assert x.numeric_max is None, f"Expected None, got {x.numeric_max}"
    assert x.numeric_mean is None, f"Expected None, got {x.numeric_mean}"
    assert x.numeric_median is None, f"Expected None, got {x.numeric_median}"


def test_profiling_unicode_headers() -> None:
    """F17: Non-ASCII column names must survive the pipeline and appear in the report."""
    df = pl.read_csv(FIXTURES_DIR / "unicode_headers.csv")

    # Verify the fixture loaded correctly
    assert "价格" in df.columns
    assert "année" in df.columns
    assert "名前" in df.columns

    service = ProfilingService()
    profile = service.profile(df, "ds_unicode01")

    col_names = {c.name for c in profile.columns}
    assert "价格" in col_names, f"Unicode column '价格' missing from profile: {col_names}"
    assert "année" in col_names, f"Unicode column 'année' missing from profile: {col_names}"
    assert "名前" in col_names, f"Unicode column '名前' missing from profile: {col_names}"
    assert profile.row_count == 3

