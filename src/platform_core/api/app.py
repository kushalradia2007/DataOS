"""FastAPI Application."""
import json
import tempfile
from pathlib import Path
from typing import Annotated, Any

import polars as pl
from fastapi import FastAPI, File, HTTPException, Request, UploadFile

from platform_core.orchestration.pipeline import run_pipeline
from platform_core.shared.exceptions import DomainError
from platform_core.shared.ids import validate_dataset_id

app = FastAPI(title="Data Platform API")

MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MiB
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".parquet"}
DATA_DIR = Path("data").resolve()
REPORTS_DIR = (DATA_DIR / "reports").resolve()
STAGING_DIR = (DATA_DIR / "staging").resolve()

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}

@app.post("/v1/datasets/upload")
def upload_dataset(request: Request, file: Annotated[UploadFile, File(...)]) -> dict[str, Any]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")
        
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Request Entity Too Large")

    # Secure filename extraction
    file_path = Path(file.filename)
    suffix = file_path.suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {suffix}")

    # Single try/finally covers both streaming write and pipeline execution
    # so temp file is always cleaned up, even on unexpected read errors.
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = Path(tmp.name)
            bytes_read = 0
            while chunk := file.file.read(8192):
                bytes_read += len(chunk)
                if bytes_read > MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail="Request Entity Too Large")
                tmp.write(chunk)

        report = run_pipeline(tmp_path, original_file_name=file_path.name)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException:
        raise
    except OSError as e:
        raise HTTPException(status_code=500, detail="Internal server error") from e
    finally:
        if tmp_path is not None and tmp_path.exists():
            tmp_path.unlink()
            
    return report

@app.get("/v1/datasets/{dataset_id}/report")
def get_report(dataset_id: str) -> dict[str, Any]:
    if not validate_dataset_id(dataset_id):
        raise HTTPException(status_code=400, detail="Invalid dataset ID")
        
    report_path = (REPORTS_DIR / f"{dataset_id}.json").resolve()
    if not report_path.is_relative_to(REPORTS_DIR):
        raise HTTPException(status_code=400, detail="Invalid path traversal")
        
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
        
    result: dict[str, Any] = json.loads(report_path.read_text(encoding="utf-8"))
    return result

@app.get("/v1/datasets/{dataset_id}/preview")
def get_preview(dataset_id: str) -> list[dict[str, Any]]:
    if not validate_dataset_id(dataset_id):
        raise HTTPException(status_code=400, detail="Invalid dataset ID")
        
    staged_path = (STAGING_DIR / f"{dataset_id}.parquet").resolve()
    if not staged_path.is_relative_to(STAGING_DIR):
        raise HTTPException(status_code=400, detail="Invalid path traversal")

    if not staged_path.exists():
        raise HTTPException(status_code=404, detail="Staged dataset not found")
        
    try:
        df = pl.read_parquet(staged_path).head(100)
        rows: list[dict[str, Any]] = df.to_dicts()
        return rows
    except (OSError, ValueError, pl.exceptions.ComputeError) as e:
        raise HTTPException(status_code=500, detail=f"Failed to preview data: {e}") from e
