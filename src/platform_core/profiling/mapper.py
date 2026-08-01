"""Mapper for profiling results."""
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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

logger = logging.getLogger(__name__)

def run_and_map_profile(
    df_pandas: Any,
    exact_stats: dict[str, Any],
    dataset_id: str,
    sampling_applied: bool,
    html_report_path: Path | None = None
) -> DatasetProfile:
    """Run data_profiling and map to domain models."""
    from data_profiling import ProfileReport
    
    profile = ProfileReport(df_pandas, minimal=True)
    
    if html_report_path:
        try:
            profile.to_file(str(html_report_path))
        except Exception:
            logger.warning("HTML report generation failed: %s", html_report_path, exc_info=True)
        
    desc = profile.get_description()
    
    columns_profile = []
    
    variables = desc.variables if hasattr(desc, "variables") else {}
    for i, (col_name, exact_col_stats) in enumerate(exact_stats["columns"].items()):
        var_desc = variables.get(col_name, {})
        
        numeric_stats = None
        if "mean" in var_desc and "50%" in var_desc:
            # Finding 19: Use exact min/max if present in exact_col_stats, else fallback to sampled profile stats
            exact_min = exact_col_stats.get("min")
            exact_max = exact_col_stats.get("max")
            numeric_stats = {
                "mean": float(var_desc["mean"]),
                "median": float(var_desc["50%"]),
                "min": float(exact_min if exact_min is not None else var_desc.get("min", 0.0)),
                "max": float(exact_max if exact_max is not None else var_desc.get("max", 0.0)),
                "std": float(var_desc.get("std", 0.0))
            }
            
        top_values = None
        if "value_counts_without_nan" in var_desc:
            vc = var_desc["value_counts_without_nan"]
            try:
                if hasattr(vc, "head"):
                    top_values = {str(k): int(v) for k, v in vc.head(10).items()}
                elif isinstance(vc, dict):
                    top_values = {str(k): int(v) for j, (k, v) in enumerate(vc.items()) if j < 10}
            except Exception as e:  # noqa: BLE001
                logger.debug("value_counts extraction failed for %s: %s", col_name, e)
                
        # Fix list type for sample values
        sample_values: list[str | int | float | bool | None] = list(top_values.keys()) if top_values else []
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
        
    summary: dict[str, object] = {}
    if sampling_applied:
        summary["sampling_applied"] = True
        summary["sample_size"] = 10000

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
