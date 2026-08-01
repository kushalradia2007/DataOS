"""Profiling service."""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import polars as pl

from platform_core.domain.models.profile import DatasetProfile
from platform_core.profiling.fallback import fallback_profile
from platform_core.profiling.mapper import run_and_map_profile
from platform_core.shared.dataframe import to_pandas

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ExactStats:
    """Immutable exact statistics computed from the full dataset before sampling."""
    row_count: int
    column_count: int
    duplicate_rows: int
    memory_usage_bytes: int
    columns: dict[str, dict[str, Any]]

    @classmethod
    def from_dataframe(cls, df: pl.DataFrame) -> "ExactStats":
        return cls(
            row_count=df.height,
            column_count=df.width,
            duplicate_rows=df.height - df.unique().height,
            memory_usage_bytes=int(df.estimated_size()),
            columns={
                col: {
                    "null_count": df[col].null_count(),
                    "n_unique": df[col].n_unique(),
                    "dtype": str(df[col].dtype),
                    "min": df[col].min() if df[col].dtype.is_numeric() else None,
                    "max": df[col].max() if df[col].dtype.is_numeric() else None,
                }
                for col in df.columns
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "row_count": self.row_count,
            "column_count": self.column_count,
            "duplicate_rows": self.duplicate_rows,
            "memory_usage_bytes": self.memory_usage_bytes,
            "columns": self.columns
        }


class ProfilingService:
    """Service to profile a dataset."""
    
    def __init__(self, reports_dir: Path = Path("data/reports")):
        self.reports_dir = reports_dir
        
    def profile(self, df: pl.DataFrame, dataset_id: str) -> DatasetProfile:
        """Profile a dataframe and return a DatasetProfile.
        
        Args:
            df: The staged Polars dataframe.
            dataset_id: The ID of the dataset.
            
        Returns:
            The DatasetProfile.
        """
        # 1. Exact full-data stats
        # O(n) scans - fast even on millions of rows
        exact_stats = ExactStats.from_dataframe(df)
        
        # 2. Sampling
        sampling_applied = False
        original_df = df
        if df.height > 10000:
            df = df.sample(n=10000, seed=42)
            sampling_applied = True
            
        try:
            # 3. Boundary conversion to pandas
            df_pandas = to_pandas(df)
            
            # 4. Determine HTML Report Path
            html_report_path = None
            try:
                self.reports_dir.mkdir(parents=True, exist_ok=True)
                html_report_path = self.reports_dir / f"{dataset_id}_profile.html"
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Failed to setup HTML report dir: {e}")
                
            # 5. Extract and Map (mapper handles ProfileReport internally to isolate imports)
            dataset_profile = run_and_map_profile(
                df_pandas=df_pandas,
                exact_stats=exact_stats.to_dict(),
                dataset_id=dataset_id,
                sampling_applied=sampling_applied,
                html_report_path=html_report_path
            )
            
            if html_report_path and html_report_path.exists():
                dataset_profile.summary["html_report_path"] = str(html_report_path)
            else:
                dataset_profile.summary["html_report_path"] = None
                
            return dataset_profile
            
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Profiling library failed, using fallback: {e}")
            return fallback_profile(
                df=original_df,
                dataset_id=dataset_id,
                exact_stats=exact_stats.to_dict(),
                sampling_applied=sampling_applied
            )
