"""Fallback for profiling when library fails."""
from datetime import UTC
from typing import Any

import polars as pl

from platform_core.domain.enums import ColumnRole, PhysicalType, SemanticType
from platform_core.domain.models.column import ColumnProfile
from platform_core.domain.models.profile import DatasetProfile


def _map_physical_type(dtype_str: str) -> PhysicalType:
    dtype_str = dtype_str.lower()
    if "int" in dtype_str:
        return PhysicalType.INTEGER
    if "float" in dtype_str:
        return PhysicalType.FLOAT
    if "bool" in dtype_str:
        return PhysicalType.BOOLEAN
    if "datetime" in dtype_str or "date" in dtype_str:
        return PhysicalType.DATETIME
    if "str" in dtype_str or "utf8" in dtype_str:
        return PhysicalType.STRING
    return PhysicalType.UNKNOWN

def fallback_profile(
    df: pl.DataFrame,
    dataset_id: str,
    exact_stats: dict[str, Any],
    sampling_applied: bool
) -> DatasetProfile:
    """Generate basic profiling stats using pure Polars when library fails."""
    
    columns_profile = []
    
    for i, (col_name, exact_col_stats) in enumerate(exact_stats["columns"].items()):
        sample_values: list[str | int | float | bool | None] = []
        try:
            s = df[col_name].drop_nulls().unique()
            sample_values = s.head(5).to_list()
        except Exception:  # noqa: BLE001, S110
            pass
            
        numeric_stats = None
        dtype_str = exact_col_stats["dtype"].lower()
        if "int" in dtype_str or "float" in dtype_str:
            try:
                s = df[col_name]
                s_mean = s.mean()
                s_median = s.median()
                s_std = s.std()
                
                exact_min = exact_col_stats.get("min")
                exact_max = exact_col_stats.get("max")
                
                s_min = exact_min if exact_min is not None else s.min()
                s_max = exact_max if exact_max is not None else s.max()
                
                numeric_stats = {
                    "mean": float(s_mean) if s_mean is not None else None,
                    "median": float(s_median) if s_median is not None else None,
                    "min": float(s_min) if s_min is not None else None,
                    "max": float(s_max) if s_max is not None else None,
                    "std": float(s_std) if s_std is not None else None
                }
            except Exception:  # noqa: BLE001, S110
                pass
                
        top_values = None
        try:
            vc = df[col_name].value_counts(sort=True).head(10)
            if len(vc) > 0:
                top_values = {str(row[0]): int(row[1]) for row in vc.iter_rows()}
        except Exception:  # noqa: BLE001, S110
            pass

        physical_type = _map_physical_type(exact_col_stats["dtype"])
        row_count = exact_stats["row_count"]
        
        columns_profile.append(ColumnProfile(
            name=col_name,
            position=i,
            physical_type=physical_type,
            semantic_type=SemanticType.UNKNOWN,
            role=ColumnRole.FEATURE,
            total_count=row_count,
            non_null_count=row_count - exact_col_stats["null_count"],
            null_count=exact_col_stats["null_count"],
            null_percentage=(exact_col_stats["null_count"] / row_count * 100.0) if row_count > 0 else 0.0,
            unique_count=exact_col_stats["n_unique"],
            unique_percentage=(exact_col_stats["n_unique"] / row_count * 100.0) if row_count > 0 else 0.0,
            sample_values=sample_values,
            inferred_type_confidence=1.0,
            alternative_type_candidates=[],
            numeric_min=numeric_stats.get("min") if numeric_stats else None,
            numeric_max=numeric_stats.get("max") if numeric_stats else None,
            numeric_mean=numeric_stats.get("mean") if numeric_stats else None,
            numeric_median=numeric_stats.get("median") if numeric_stats else None,
            most_common_values=[{"value": str(k), "count": int(v)} for k, v in (top_values or {}).items()],
            detected_formats=[]
        ))
        
    summary: dict[str, object] = {"fallback_used": True}
    if sampling_applied:
        summary["sampling_applied"] = True
        summary["sample_size"] = 10000

    from datetime import datetime

    return DatasetProfile(
        dataset_id=dataset_id,
        file_name=f"{dataset_id}.parquet",
        file_format="parquet",
        created_at=datetime.now(UTC).isoformat(),
        row_count=exact_stats["row_count"],
        column_count=exact_stats["column_count"],
        duplicate_row_count=exact_stats["duplicate_rows"],
        memory_usage_bytes=exact_stats["memory_usage_bytes"],
        columns=columns_profile,
        validation_issues=[],
        quality_score=1.0,
        summary=summary
    )
