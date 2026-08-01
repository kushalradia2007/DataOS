"""Integration tests for the API and pipeline."""
from pathlib import Path

from fastapi.testclient import TestClient

from platform_core.api.app import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_e2e_pipeline():
    fixtures_dir = Path("tests/fixtures")
    dirty_sales_path = fixtures_dir / "dirty_sales.csv"
    
    assert dirty_sales_path.exists(), "Fixture missing"
    
    with open(dirty_sales_path, "rb") as f:
        # 1. Upload
        response = client.post(
            "/v1/datasets/upload",
            files={"file": ("dirty_sales.csv", f, "text/csv")}
        )
        
    assert response.status_code == 200, response.text
    report = response.json()
    
    # Assert report shape
    assert report["schema_version"] == "1.0"
    assert "dataset_id" in report
    dataset_id = report["dataset_id"]
    
    assert report["file_name"] == "dirty_sales.csv"
    assert report["row_count"] == 5
    
    columns = {c["name"]: c for c in report["columns"]}
    assert "id" in columns
    assert "sales" in columns
    assert "category" in columns
    
    # Assert validation issues are present (dirty_sales has duplicated row and missing sales)
    issues = report["validation_issues"]
    issue_codes = [issue["code"] for issue in issues]
    assert "duplicate_rows" in issue_codes
    assert "high_null_rate" in issue_codes # Because sales has 1 null out of 5 (20% > 10%)
    
    # 2. Get Report
    report_response = client.get(f"/v1/datasets/{dataset_id}/report")
    assert report_response.status_code == 200
    assert report_response.json()["dataset_id"] == dataset_id
    
    # 3. Get Preview
    preview_response = client.get(f"/v1/datasets/{dataset_id}/preview")
    assert preview_response.status_code == 200
    preview_data = preview_response.json()
    assert len(preview_data) == 5
    assert "id" in preview_data[0]

def test_upload_empty_file() -> None:
    # 0 byte file
    response = client.post(
        "/v1/datasets/upload",
        files={"file": ("empty.csv", b"", "text/csv")}
    )
    assert response.status_code == 400
    assert "No columns" in response.json()["detail"] or "empty" in response.json()["detail"].lower() or "no data" in response.json()["detail"].lower()

def test_upload_unsupported_format() -> None:
    response = client.post(
        "/v1/datasets/upload",
        files={"file": ("script.sh", b"echo hello", "text/plain")}
    )
    assert response.status_code == 400
    assert "Unsupported format" in response.json()["detail"]

def test_upload_oversized_file() -> None:
    # Create fake 51MB file
    # We patch MAX_UPLOAD_BYTES in the app temporarily
    from platform_core.api import app as api_app
    old_max = api_app.MAX_UPLOAD_BYTES
    api_app.MAX_UPLOAD_BYTES = 100
    
    try:
        response = client.post(
            "/v1/datasets/upload",
            files={"file": ("large.csv", b"a" * 150, "text/csv")}
        )
        assert response.status_code == 413
        assert "Too Large" in response.json()["detail"]
    finally:
        api_app.MAX_UPLOAD_BYTES = old_max

def test_dataset_id_validation() -> None:
    # Invalid character test (simulating traversal attempt without slashes)
    response = client.get("/v1/datasets/..ds_12345678/report")
    assert response.status_code == 400
    
    # Regex test (invalid ID format)
    response = client.get("/v1/datasets/ds_12345/report")
    assert response.status_code == 400


def test_path_containment_sibling_prefix() -> None:
    """R2: Prove that a sibling-directory prefix attack is rejected by is_relative_to.

    '/app/data/reports_evil/' starts with '/app/data/reports' (str.startswith would pass)
    but is NOT relative to '/app/data/reports' (is_relative_to correctly rejects).
    """
    from unittest.mock import patch

    # We need validate_dataset_id to pass so we can reach the path check.
    # Use a valid-format ID but point REPORTS_DIR to a controlled location.
    from platform_core.api import app as api_app

    fake_reports = Path("/app/data/reports").resolve()
    # The sibling: /app/data/reports_evil/ds_aabbccdd.json would pass startswith
    # but the endpoint constructs REPORTS_DIR / f"{dataset_id}.json" so we need
    # to verify the guard logic directly. We'll set REPORTS_DIR to a path where
    # the resolved child escapes via symlink or by constructing a non-child.
    # Simplest approach: verify the actual code path rejects non-relative paths.
    original_reports_dir = api_app.REPORTS_DIR
    try:
        # Set REPORTS_DIR to a path, and make the resolved file point outside it.
        # Since the endpoint does (REPORTS_DIR / f"{dataset_id}.json").resolve(),
        # we'll mock resolve to return a sibling path.
        evil_path = fake_reports.parent / "reports_evil" / "ds_aabbccdd.json"
        with patch.object(Path, "resolve", return_value=evil_path):
            response = client.get("/v1/datasets/ds_aabbccdd/report")
        assert response.status_code == 400
        assert "path traversal" in response.json()["detail"].lower()
    finally:
        api_app.REPORTS_DIR = original_reports_dir


def test_upload_tmp_cleanup_on_read_error() -> None:
    """R3: Temp file must be cleaned up when file.file.read() raises during streaming."""
    import glob
    import tempfile
    from unittest.mock import MagicMock

    tmp_dir = tempfile.gettempdir()

    # Count .csv temp files before the request
    pre_files = set(glob.glob(str(Path(tmp_dir) / "*.csv")))

    # Create a mock file whose read() raises on the first call
    mock_file = MagicMock()
    mock_file.filename = "test.csv"
    mock_file.file.read.side_effect = OSError("simulated network disconnect")

    # We need to intercept at the ASGI level, so we use the TestClient
    # and patch the read call inside the streaming loop.
    # The simplest approach: upload a real file but patch the read method.
    response = client.post(
        "/v1/datasets/upload",
        files={"file": ("test.csv", b"a,b\n1,2\n", "text/csv")},
    )
    # That uploads fine. For the actual test, we need to trigger a read error.
    # Let's patch at a lower level.

    import io

    class FailingReader(io.BytesIO):
        """A file-like that fails on the first read call."""
        def __init__(self) -> None:
            super().__init__(b"")
        def read(self, n: int = -1) -> bytes:
            raise OSError("simulated network disconnect")

    response = client.post(
        "/v1/datasets/upload",
        files={"file": ("crash.csv", FailingReader(), "text/csv")},
    )
    # The OSError from read() should be caught and produce HTTP 500
    assert response.status_code in (400, 500)

    # Verify no orphan temp files were left behind
    post_files = set(glob.glob(str(Path(tmp_dir) / "*.csv")))
    orphans = post_files - pre_files
    assert len(orphans) == 0, f"Orphan temp files left behind: {orphans}"
