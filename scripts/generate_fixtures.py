from pathlib import Path

fixtures_dir = Path("tests/fixtures")
fixtures_dir.mkdir(parents=True, exist_ok=True)

# utf8.csv
(fixtures_dir / "utf8.csv").write_text("col1,col2\n1,añejo\n3,4", encoding="utf-8")

# utf16.csv
(fixtures_dir / "utf16.csv").write_text("col1,col2\n1,2\n3,4", encoding="utf-16")

# semicolon.csv
(fixtures_dir / "semicolon.csv").write_text("col1;col2\n1;2\n3;4", encoding="utf-8")

# tab.csv
(fixtures_dir / "tab.csv").write_text("col1\tcol2\n1\t2\n3\t4", encoding="utf-8")

# bom.csv
(fixtures_dir / "bom.csv").write_text("col1,col2\n1,2\n3,4", encoding="utf-8-sig")

# malformed.csv
(fixtures_dir / "malformed.csv").write_text("col1,col2\n1,2\n3,4,5\n6", encoding="utf-8")

# empty.csv
(fixtures_dir / "empty.csv").write_text("", encoding="utf-8")

# quoted_delim.csv
(fixtures_dir / "quoted_delim.csv").write_text('col1,col2\n1,2\n3,4\n"5,6",7\n8,"9,10"', encoding="utf-8")

# dirty_sales.csv
dirty_sales = (
    "id,sales,category\n"
    "1,100.5,A\n"
    "2,,B\n"
    "3,200.0,A\n"
    "3,200.0,A\n"
    "4,150.0,C\n"
)
(fixtures_dir / "dirty_sales.csv").write_text(dirty_sales, encoding="utf-8")

# mixed_types.csv
mixed_types = (
    "a,b,c\n"
    "1,x,true\n"
    "2,y,false\n"
    "3,z,\n"
)
(fixtures_dir / "mixed_types.csv").write_text(mixed_types, encoding="utf-8")

import json

expected_stats = {
    "dirty_sales": {
        "row_count": 5,
        "duplicate_rows": 1,
        "null_counts": {"id": 0, "sales": 1, "category": 0},
        "n_unique": {"id": 4, "sales": 4, "category": 3}  # sales has 3 unique numbers + 1 null (Polars n_unique includes null)
    },
    "mixed_types": {
        "row_count": 3,
        "duplicate_rows": 0,
        "null_counts": {"a": 0, "b": 0, "c": 1},
        "n_unique": {"a": 3, "b": 3, "c": 3} # true, false, null
    }
}
(fixtures_dir / "expected_stats.json").write_text(json.dumps(expected_stats, indent=2), encoding="utf-8")
