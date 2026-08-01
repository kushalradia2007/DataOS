# Dataset Profile & Report Schema Contract (v1.0)

This contract defines the exact JSON schema and Pydantic models for the Phase 1 Data Platform report output.

## Schema Version
`"schema_version": "1.0"`

## Stable Report Schema Definition

```json
{
  "schema_version": "1.0",
  "dataset_id": "ds_01JX9R4B7ZK",
  "file_name": "dirty_sales.csv",
  "file_format": "csv",
  "created_at": "2026-07-29T10:00:00Z",
  "row_count": 1000,
  "column_count": 8,
  "duplicate_row_count": 12,
  "memory_usage_bytes": 65536,
  "quality_score": 85.0,
  "columns": [
    {
      "name": "transaction_id",
      "position": 0,
      "physical_type": "string",
      "semantic_type": "identifier",
      "role": "identifier",
      "total_count": 1000,
      "non_null_count": 1000,
      "null_count": 0,
      "null_percentage": 0.0,
      "unique_count": 1000,
      "unique_percentage": 100.0,
      "sample_values": ["TX-1001", "TX-1002"],
      "inferred_type_confidence": 0.99,
      "alternative_type_candidates": [
        {
          "type": "categorical",
          "confidence": 0.2,
          "evidence": ["Low cardinality relative to size"]
        }
      ],
      "numeric_min": null,
      "numeric_max": null,
      "numeric_mean": null,
      "numeric_median": null,
      "most_common_values": [],
      "detected_formats": ["TX-{integer}"]
    }
  ],
  "validation_issues": [
    {
      "code": "high_null_rate",
      "severity": "warning",
      "title": "High null rate in column 'discount'",
      "message": "Column 'discount' has 15.0% null values, exceeding the 10.0% threshold.",
      "column_name": "discount",
      "affected_rows": 150,
      "affected_percentage": 15.0,
      "evidence": {
        "null_count": 150,
        "null_percentage": 0.15,
        "threshold": 0.1
      },
      "recommended_action": "Consider imputing missing values or dropping the column.",
      "auto_fix_available": false
    }
  ],
  "summary": {
    "html_report_path": "data/reports/ds_01JX9R4B7ZK_profile.html"
  }
}
```

## Domain Enums

- **PhysicalType**: `integer`, `float`, `boolean`, `string`, `datetime`, `unknown`
- **SemanticType**: `numeric`, `categorical`, `datetime`, `text`, `identifier`, `boolean`, `unknown`
- **ColumnRole**: `feature`, `target_candidate`, `identifier`, `datetime`, `ignore`
- **Severity**: `info`, `warning`, `error`
- **IssueCode**: `high_null_rate`, `duplicate_rows`, `constant_column`, `mixed_type`

## FastAPI Endpoints

| Endpoint | Method | Description |
| --- | --- | --- |
| `/health` | GET | Healthcheck returning `{"status": "healthy"}` |
| `/v1/datasets/upload` | POST | Multipart upload file -> runs ingestion, staging, profiling, inference, validation -> returns report JSON |
| `/v1/datasets/{id}/report` | GET | Retrieves stored dataset report JSON |
| `/v1/datasets/{id}/preview` | GET | Returns first 100 rows preview from staged Parquet |
