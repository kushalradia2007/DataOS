"""CSV reader module."""
import csv
import logging
from pathlib import Path

import polars as pl
from charset_normalizer import from_bytes

from platform_core.ingestion.readers.base import BaseReader, IngestionMetadata
from platform_core.shared.exceptions import EmptyFileError

logger = logging.getLogger(__name__)


class CSVReader(BaseReader):
    """Reads CSV files with auto-detection of encoding and delimiter."""
    
    def read(self, file_path: Path) -> tuple[pl.DataFrame, IngestionMetadata]:
        if not file_path.exists() or file_path.stat().st_size == 0:
            raise EmptyFileError(f"File is empty or does not exist: {file_path}")
            
        # Detect encoding
        with open(file_path, "rb") as f:
            raw_sample = f.read(10000)
            
        detection = from_bytes(raw_sample).best()
        encoding = (detection.encoding if detection else "utf-8").replace("_", "-")
        
        # Decode sample for sniffing
        try:
            decoded_sample = raw_sample.decode(encoding)
        except UnicodeDecodeError:  # pragma: no cover
            encoding = "utf-8"
            decoded_sample = raw_sample.decode(encoding, errors="replace")
            
        # Strip BOM if present
        if encoding.lower() == "utf-8-sig":
            encoding = "utf-8"
            
        # Detect delimiter and header
        sniffer = csv.Sniffer()
        delimiter = ","
        has_header = True
        try:
            dialect = sniffer.sniff(decoded_sample, delimiters=",;\t|")
            delimiter = dialect.delimiter
            has_header = sniffer.has_header(decoded_sample)
        except csv.Error:
            # Fallback if sniffing fails
            pass
            
        warnings = []
        
        # Polars native read
        try:
            # If not utf-8, we transcode in memory. For Phase 1 this is acceptable.
            source: bytes | str
            if encoding.lower() not in ("utf-8", "ascii"):
                content = file_path.read_text(encoding=encoding)
                source = content.encode("utf-8")
            else:
                source = str(file_path)
                
            df = pl.read_csv(
                source,
                separator=delimiter,
                has_header=has_header,
                ignore_errors=True,
                truncate_ragged_lines=True
            )
            
            # Simple check for malformed rows if any were skipped
            # A strict parse would fail if malformed rows exist
            try:
                pl.read_csv(
                    source,
                    separator=delimiter,
                    has_header=has_header,
                )
            except pl.exceptions.ComputeError:
                warnings.append("Malformed rows detected and skipped or truncated.")
                
        except Exception as e:
            # Catch-all for other parsing errors
            logger.warning("CSV parsing failed for %s", file_path, exc_info=True)
            warnings.append(f"Parsing issues encountered: {e}")
            df = pl.DataFrame()
            
        if df.height == 0 and df.width == 0:
            raise EmptyFileError(f"No valid data found in file: {file_path}")
            
        metadata = IngestionMetadata(
            encoding=encoding,
            delimiter=delimiter,
            row_count=df.height,
            column_count=df.width,
            warnings=warnings
        )
        
        return df, metadata
