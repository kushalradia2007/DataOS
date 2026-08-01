"""Integration tests for staging."""
from pathlib import Path

from platform_core.ingestion.readers.csv_reader import CSVReader
from platform_core.ingestion.readers.parquet_reader import ParquetReader
from platform_core.ingestion.staging import stage_dataset

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

def test_csv_to_stage(tmp_path: Path) -> None:
    # 1. Read CSV
    csv_file = FIXTURES_DIR / "utf8.csv"
    csv_reader = CSVReader()
    df, _meta = csv_reader.read(csv_file)
    
    # 2. Stage the dataset
    staging_dir = tmp_path / "staging"
    result = stage_dataset(df, csv_file, staging_dir)
    
    # Ensure the file was created and hash/id are present
    assert result.dataset_id.startswith("ds_")
    assert result.file_hash is not None
    assert Path(result.staged_path).exists()
    
    # 3. Reload from staging using ParquetReader
    parquet_reader = ParquetReader()
    reloaded_df, reloaded_meta = parquet_reader.read(Path(result.staged_path))
    
    # 4. Assert identical DataFrame
    assert df.equals(reloaded_df)
    assert reloaded_meta.row_count == df.height
    assert reloaded_meta.column_count == df.width
