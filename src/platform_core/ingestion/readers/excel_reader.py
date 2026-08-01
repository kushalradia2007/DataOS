"""Excel reader module."""
import csv
from pathlib import Path

import polars as pl

from platform_core.ingestion.readers.base import BaseReader, IngestionMetadata
from platform_core.shared.exceptions import EmptyFileError


class ExcelReader(BaseReader):
    """Reads Excel files using openpyxl engine."""
    
    def read(self, file_path: Path) -> tuple[pl.DataFrame, IngestionMetadata]:
        if not file_path.exists() or file_path.stat().st_size == 0:
            raise EmptyFileError(f"File is empty or does not exist: {file_path}")
            
        warnings: list[str] = []
        
        try:
            # Sniff for header by reading first few rows as data
            df_head = pl.read_excel(
                file_path, 
                engine="openpyxl", 
                has_header=False, 
                # Just read 10 rows to sniff
                read_options={"n_rows": 10}
            )
            if df_head.height == 0:
                raise EmptyFileError("Excel file has no data rows.")
                
            sample_csv = df_head.write_csv()
            sniffer = csv.Sniffer()
            has_header = sniffer.has_header(sample_csv)
        except (csv.Error, OSError, ValueError) as e:
            warnings.append(f"Header detection failed: {e}")
            has_header = True
            
        try:
            df = pl.read_excel(
                file_path,
                engine="openpyxl",
                has_header=has_header
            )
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
