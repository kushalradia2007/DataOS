"""Parquet reader module."""
from pathlib import Path

import polars as pl

from platform_core.ingestion.readers.base import BaseReader, IngestionMetadata
from platform_core.shared.exceptions import EmptyFileError


class ParquetReader(BaseReader):
    """Reads Parquet files using native Polars/PyArrow engine."""
    
    def read(self, file_path: Path) -> tuple[pl.DataFrame, IngestionMetadata]:
        if not file_path.exists() or file_path.stat().st_size == 0:
            raise EmptyFileError(f"File is empty or does not exist: {file_path}")
            
        warnings: list[str] = []
        
        try:
            df = pl.read_parquet(file_path)
        except (OSError, ValueError, pl.exceptions.ComputeError) as e:
            warnings.append(f"Parsing issues encountered: {e}")
            df = pl.DataFrame()
            
        if df.height == 0 and df.width == 0:
            raise EmptyFileError(f"No valid data found in file: {file_path}")
            
        metadata = IngestionMetadata(
            encoding=None,
            delimiter=None,
            row_count=df.height,
            column_count=df.width,
            warnings=warnings
        )
        
        return df, metadata
