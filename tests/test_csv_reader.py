from pathlib import Path

import pytest

from platform_core.ingestion.readers.csv_reader import CSVReader
from platform_core.shared.exceptions import EmptyFileError

FIXTURES_DIR = Path(__file__).parent / "fixtures"

@pytest.fixture
def reader() -> CSVReader:
    return CSVReader()

def test_utf8(reader: CSVReader) -> None:
    df, meta = reader.read(FIXTURES_DIR / "utf8.csv")
    assert df.height == 2
    assert meta.encoding.lower() == "utf-8"
    assert meta.delimiter == ","
    assert len(meta.warnings) == 0

def test_utf16(reader: CSVReader) -> None:
    df, meta = reader.read(FIXTURES_DIR / "utf16.csv")
    assert df.height == 2
    assert "utf-16" in meta.encoding.lower()
    assert meta.delimiter == ","

def test_semicolon(reader: CSVReader) -> None:
    df, meta = reader.read(FIXTURES_DIR / "semicolon.csv")
    assert df.height == 2
    assert meta.delimiter == ";"

def test_tab(reader: CSVReader) -> None:
    df, meta = reader.read(FIXTURES_DIR / "tab.csv")
    assert df.height == 2
    assert meta.delimiter == "\t"

def test_bom(reader: CSVReader) -> None:
    df, meta = reader.read(FIXTURES_DIR / "bom.csv")
    assert df.height == 2
    assert meta.encoding.lower() == "utf-8"
    assert meta.delimiter == ","
    assert "col1" in df.columns

def test_malformed(reader: CSVReader) -> None:
    _, meta = reader.read(FIXTURES_DIR / "malformed.csv")
    # truncate_ragged_lines drops the extra columns but doesn't drop the row by default in polars,
    # wait, if ignore_errors=True, some lines may be dropped.
    # Our simple check tests if pl.read_csv without ignore_errors fails, and appends a warning.
    assert len(meta.warnings) > 0
    assert any("Malformed rows detected" in w for w in meta.warnings)

def test_empty(reader: CSVReader) -> None:
    with pytest.raises(EmptyFileError):
        reader.read(FIXTURES_DIR / "empty.csv")

def test_quoted_delim(reader: CSVReader) -> None:
    df, meta = reader.read(FIXTURES_DIR / "quoted_delim.csv")
    assert df.height in (4, 5)
    assert meta.delimiter == ","
    # Check that quoted commas didn't split the column
    assert df.width == 2

def test_nonexistent_file(reader: CSVReader) -> None:
    with pytest.raises(EmptyFileError):
        reader.read(FIXTURES_DIR / "does_not_exist.csv")


def test_csv_parse_error_logging_regression(reader: CSVReader, tmp_path: Path) -> None:
    """R1 regression: logger must be defined; parse errors must not raise NameError."""
    from unittest.mock import patch

    # Create a real file so the reader passes the existence + encoding checks
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text("a,b\n1,2\n", encoding="utf-8")

    # Mock pl.read_csv to raise (simulating a parsing failure).
    # Before the fix, this branch raised NameError because logger was undefined.
    with patch(
        "platform_core.ingestion.readers.csv_reader.pl.read_csv",
        side_effect=Exception("simulated parse failure"),
    ), pytest.raises(EmptyFileError, match="No valid data found"):
        reader.read(csv_file)


def test_csv_parse_error_logged_and_raises(reader: CSVReader, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """R1: Verify the original exception is logged at WARNING with exc_info, and EmptyFileError propagates."""
    import logging
    from unittest.mock import patch

    csv_file = tmp_path / "bad.csv"
    csv_file.write_text("a,b\n1,2\n", encoding="utf-8")

    with (
        patch(
            "platform_core.ingestion.readers.csv_reader.pl.read_csv",
            side_effect=Exception("simulated parse failure"),
        ),
        caplog.at_level(logging.WARNING, logger="platform_core.ingestion.readers.csv_reader"),
        pytest.raises(EmptyFileError, match="No valid data found"),
    ):
        reader.read(csv_file)

    # Verify original error context is preserved in logs
    assert any("simulated parse failure" in r.message or "simulated parse failure" in str(r.exc_info) for r in caplog.records), \
        f"Expected parse failure logged; got: {[r.message for r in caplog.records]}"
    # Verify exc_info was set (traceback attached)
    assert any(r.exc_info is not None and r.exc_info[1] is not None for r in caplog.records), \
        "Expected exc_info=True to attach the original exception traceback"
