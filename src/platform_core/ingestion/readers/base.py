"""Base classes for file readers."""
from abc import ABC, abstractmethod
from pathlib import Path

import polars as pl
from pydantic import BaseModel


class IngestionMetadata(BaseModel):
    """Metadata about the ingested file."""
    encoding: str | None = None
    delimiter: str | None = None
    row_count: int
    column_count: int
    warnings: list[str]

class BaseReader(ABC):
    """Base class for all data file readers."""
    
    @abstractmethod
    def read(self, file_path: Path) -> tuple[pl.DataFrame, IngestionMetadata]:
        """Read a file and return a Polars DataFrame with metadata.
        
        Args:
            file_path: Path to the file to read.
            
        Returns:
            Tuple of DataFrame and IngestionMetadata.
            
        Raises:
            EmptyFileError: If the file is empty.
        """
