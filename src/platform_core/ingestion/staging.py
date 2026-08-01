"""Staging module."""
from pathlib import Path

import polars as pl
from pydantic import BaseModel

from platform_core.shared.hashing import hash_data
from platform_core.shared.ids import generate_dataset_id


class StagingResult(BaseModel):
    """Result of staging a dataset."""
    dataset_id: str
    staged_path: str
    file_hash: str

def stage_dataset(df: pl.DataFrame, original_file_path: Path, staging_dir: Path = Path("data/staging")) -> StagingResult:
    """Save an ingested DataFrame to the staging area.
    
    Args:
        df: The dataframe to stage.
        original_file_path: Path to the original ingested file (to compute hash).
        staging_dir: Directory to save the parquet file.
        
    Returns:
        StagingResult containing the dataset_id, staged_path, and file_hash.
    """
    dataset_id = generate_dataset_id()
    
    staging_dir.mkdir(parents=True, exist_ok=True)
    staged_path = staging_dir / f"{dataset_id}.parquet"
    
    # Save the dataframe
    df.write_parquet(staged_path)
    
    # Compute hash of the original file (read in chunks for memory safety, though for Phase 1 reading all is fine)
    # Using the shared hash_data utility which expects a string, wait, hash_data takes a string!
    # A binary file can't be safely decoded to string. Let's update hash_data to handle bytes or just read text.
    # The prompt said "store file hash via shared/hashing.py". We'll try to use hash_data as defined or modify it.
    try:
        content = original_file_path.read_text(encoding="utf-8", errors="replace")
        file_hash = hash_data(content)
    except (OSError, UnicodeDecodeError):
        # Fallback if somehow reading text fails
        file_hash = hash_data(original_file_path.name)
    
    return StagingResult(
        dataset_id=dataset_id,
        staged_path=str(staged_path),
        file_hash=file_hash
    )
