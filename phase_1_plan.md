## lets start building phase 1

Completed 2 steps

Let's start. Phase 1 is **Foundation & Data Ingestion** from the roadmap—the base layer that everything else depends on.[Memory](/search/9bc1adc0-7378-40f7-a8e6-0edbe230dd83)

## Phase 1 Objective

Build a robust system that accepts raw tabular data, understands its structure automatically, and validates quality without manual configuration. This is the entry point for the entire platform.[Memory](/search/746cac84-9caf-4ec9-ba9a-5080787c7164)

## Scope & Deliverables

- **Multi-format ingestion**: CSV, Excel, JSON, Parquet, SQL connections
- **Intelligent schema detection**: Auto-infer column types (numeric, categorical, datetime, ID, text) with confidence scores
- **Data validation engine**: Null counts, duplicate detection, range checks, format consistency
- **Target variable identification**: Smart detection with user confirmation UI
- **Dataset profiling**: Memory usage, row/col counts, cardinality analysis, basic statistics
- **Export layer**: Cleaned dataset + schema JSON + quality report

## Technical Stack

- **Core**: Python 3.11+, Pandas, Polars (for large files), PyArrow
- **Type inference**: Custom logic + `pandas.api.types` fallbacks
- **Validation**: Great Expectations or Pandera for declarative checks
- **API**: FastAPI for file upload endpoints
- **Storage**: Temporary parquet staging before pipeline processing

## Week 1–2 Tasks

1. Build file upload handler with streaming support for files up to 2GB
2. Implement schema inference engine with 15+ type heuristics
3. Create validation rule engine with severity levels (error/warning/info)
4. Design JSON schema output format for downstream modules
5. Build basic CLI wrapper for testing

## Success Criteria

- Ingests 95% of common tabular formats without errors
- Type inference accuracy >90% on standard business datasets
- Validation catches 100% of nulls, dupes, and obvious type mismatches
- Processing time <30s for 1M row datasets

Are you building this solo or with a team?

Prepared using Kimi K3

![](https://www.google.com/s2/favicons?sz=128&domain=perplexity.ai)

![](https://www.google.com/s2/favicons?sz=128&domain=perplexity.ai)

2 sources

i am building solo with the help of cursor and google antigravity

Getting started with solo and cursor

Good setup—solo with AI coding agents is actually ideal for Phase 1, since ingestion and schema detection are well-bounded problems where Cursor and Antigravity can generate most of the boilerplate while you focus on architecture decisions.

## Solo Build Strategy for Phase 1

## How to Split the Work

- **You own**: Architecture decisions, schema inference heuristics, the JSON contract between modules, and quality review of AI-generated code
- **Cursor handles**: FastAPI endpoints, file parsers, test scaffolding, Pandas/Polars boilerplate
- **Antigravity handles**: Multi-step tasks like "build the validation engine with these 12 rules and tests" — give it complete, self-contained specs

## Rules for Solo + AI Development

1. **Write the schema contract first yourself.** The JSON output format from Phase 1 feeds every later module (cleaning, preprocessing, feature generation, leakage detection). If AI tools invent it ad hoc, you'll rewrite Modules 2–5 later.[Memory](/search/746cac84-9caf-4ec9-ba9a-5080787c7164)
2. **One module per AI session.** Don't let agents touch the whole codebase at once—context drift causes subtle inconsistencies.
3. **Tests are your team.** With no code reviewer, require every AI-generated function to come with pytest cases. Run them before accepting.
4. **Commit daily, tag weekly.** Solo means no one catches your regressions except git.

## Suggested First Prompt for Antigravity

> "Build a Python module `ingestion/` that: (1) accepts CSV/Excel/Parquet file paths, (2) returns a Polars DataFrame, (3) handles encoding detection, delimiter sniffing, and header inference, (4) includes pytest coverage for 10 edge cases. Use Python 3.11, no global state."

## Adjusted Timeline

Solo with AI assistance, Phase 1 is realistic in **2–3 weeks** instead of 4: weeks 1–2 for ingestion + schema inference, week 3 for validation + export + testing. Don't compress further—the schema inference heuristics need real dataset testing, and that takes time, not tokens.

Want me to draft the Phase 1 folder structure and the schema JSON contract as a downloadable starter file?

Prepared using Kimi K3

![](https://www.google.com/s2/favicons?sz=128&domain=perplexity.ai)

1 source

yes detailed phase 1 folder

Exploring the detailed Phase 1 folder

Use this as the Phase 1 repository structure. It keeps ingestion, profiling, schema inference, and validation separate—so later cleaning, preprocessing, feature engineering, and leakage modules can plug in without restructuring. This is designed for your solo build with Cursor/Antigravity: small, testable modules and clear contracts.

## Repository Layout

text

auto-data-platform/
├── README.md
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
│
├── docs/
│ ├── architecture.md
│ ├── api-contracts.md
│ ├── schema-contract.md
│ ├── validation-rules.md
│ └── decisions/
│ ├── 001-use-polars-as-core-engine.md
│ └── 002-dataset-profile-contract.md
│
├── config/
│ ├── settings.yaml
│ ├── supported_formats.yaml
│ ├── validation_rules.yaml
│ └── logging.yaml
│
├── src/
│ └── platform_core/
│ ├── **init**.py
│ ├── main.py
│ ├── settings.py
│ │
│ ├── api/
│ │ ├── **init**.py
│ │ ├── app.py
│ │ ├── dependencies.py
│ │ ├── middleware.py
│ │ ├── routes/
│ │ │ ├── health.py
│ │ │ ├── datasets.py
│ │ │ └── reports.py
│ │ └── schemas/
│ │ ├── common.py
│ │ ├── dataset.py
│ │ ├── profile.py
│ │ └── error.py
│ │
│ ├── domain/
│ │ ├── **init**.py
│ │ ├── enums.py
│ │ ├── models/
│ │ │ ├── dataset.py
│ │ │ ├── column.py
│ │ │ ├── profile.py
│ │ │ ├── validation.py
│ │ │ └── lineage.py
│ │ └── contracts/
│ │ ├── ingestion.py
│ │ ├── inference.py
│ │ ├── profiling.py
│ │ └── validation.py
│ │
│ ├── ingestion/
│ │ ├── **init**.py
│ │ ├── service.py
│ │ ├── registry.py
│ │ ├── file_detector.py
│ │ ├── encoding_detector.py
│ │ ├── delimiter_detector.py
│ │ ├── header_detector.py
│ │ ├── normalizer.py
│ │ ├── staging.py
│ │ └── readers/
│ │ ├── **init**.py
│ │ ├── base.py
│ │ ├── csv_reader.py
│ │ ├── excel_reader.py
│ │ ├── json_reader.py
│ │ ├── parquet_reader.py
│ │ └── sql_reader.py
│ │
│ ├── profiling/
│ │ ├── **init**.py
│ │ ├── service.py
│ │ ├── dataset_profiler.py
│ │ ├── column_profiler.py
│ │ ├── numeric_stats.py
│ │ ├── categorical_stats.py
│ │ ├── datetime_stats.py
│ │ ├── text_stats.py
│ │ ├── missingness.py
│ │ ├── duplicates.py
│ │ ├── cardinality.py
│ │ └── sampling.py
│ │
│ ├── inference/
│ │ ├── **init**.py
│ │ ├── service.py
│ │ ├── type_inference.py
│ │ ├── semantic_inference.py
│ │ ├── confidence.py
│ │ ├── role_inference.py
│ │ └── detectors/
│ │ ├── **init**.py
│ │ ├── numeric.py
│ │ ├── categorical.py
│ │ ├── datetime.py
│ │ ├── boolean.py
│ │ ├── identifier.py
│ │ ├── email.py
│ │ ├── phone.py
│ │ ├── url.py
│ │ ├── text.py
│ │ └── target_candidate.py
│ │
│ ├── validation/
│ │ ├── **init**.py
│ │ ├── service.py
│ │ ├── rule_registry.py
│ │ ├── severity.py
│ │ ├── result_builder.py
│ │ └── rules/
│ │ ├── **init**.py
│ │ ├── base.py
│ │ ├── null_rate.py
│ │ ├── duplicate_rows.py
│ │ ├── duplicate_columns.py
│ │ ├── constant_column.py
│ │ ├── high_cardinality.py
│ │ ├── mixed_type.py
│ │ ├── invalid_numeric.py
│ │ ├── invalid_datetime.py
│ │ ├── invalid_category.py
│ │ ├── suspicious_identifier.py
│ │ └── column_name_quality.py
│ │
│ ├── orchestration/
│ │ ├── **init**.py
│ │ ├── pipeline.py
│ │ ├── run_context.py
│ │ ├── job_manager.py
│ │ └── events.py
│ │
│ ├── storage/
│ │ ├── **init**.py
│ │ ├── dataset_store.py
│ │ ├── report_store.py
│ │ ├── local_store.py
│ │ └── paths.py
│ │
│ ├── reporting/
│ │ ├── **init**.py
│ │ ├── report_builder.py
│ │ ├── json_exporter.py
│ │ └── summary_builder.py
│ │
│ └── shared/
│ ├── **init**.py
│ ├── exceptions.py
│ ├── logging.py
│ ├── hashing.py
│ ├── ids.py
│ ├── timing.py
│ └── dataframe.py
│
├── tests/
│ ├── conftest.py
│ ├── unit/
│ │ ├── ingestion/
│ │ ├── profiling/
│ │ ├── inference/
│ │ ├── validation/
│ │ ├── orchestration/
│ │ └── reporting/
│ ├── integration/
│ │ ├── test_csv_to_report.py
│ │ ├── test_excel_to_report.py
│ │ └── test_parquet_to_report.py
│ └── fixtures/
│ ├── clean_sales.csv
│ ├── dirty_sales.csv
│ ├── mixed_types.csv
│ ├── broken_dates.csv
│ ├── duplicate_rows.csv
│ ├── high_nulls.csv
│ ├── customer_data.xlsx
│ └── events.parquet
│
├── scripts/
│ ├── generate_fixtures.py
│ ├── benchmark_ingestion.py
│ └── run_local_pipeline.py
│
├── data/
│ ├── uploads/
│ ├── staging/
│ ├── processed/
│ └── reports/
│
└── notebooks/
 ├── schema_inference_experiments.ipynb
 └── profiling_benchmarks.ipynb

## Start Smaller

Do **not** build every folder on day one. Start with this reduced implementation tree, then expand only when a file has a real responsibility:

text

src/platform_core/
├── api/
│ ├── app.py
│ └── routes/datasets.py
├── domain/
│ ├── enums.py
│ └── models/
│ ├── dataset.py
│ ├── column.py
│ ├── profile.py
│ └── validation.py
├── ingestion/
│ ├── service.py
│ └── readers/
│ ├── csv_reader.py
│ ├── excel_reader.py
│ └── parquet_reader.py
├── profiling/
│ ├── service.py
│ ├── dataset_profiler.py
│ └── column_profiler.py
├── inference/
│ ├── service.py
│ └── type_inference.py
├── validation/
│ ├── service.py
│ └── rules/
│ ├── null_rate.py
│ ├── duplicate_rows.py
│ ├── constant_column.py
│ └── mixed_type.py
├── orchestration/
│ └── pipeline.py
├── reporting/
│ └── report_builder.py
└── shared/
 ├── exceptions.py
 ├── hashing.py
 └── dataframe.py

Build the reduced version first. Add specialized detectors, registries, SQL ingestion, async job management, and configurable rule systems only after the end-to-end pipeline works.

## Module Responsibilities

| Module | Owns | Must not own |
| --- | --- | --- |
| `ingestion/` | Read raw files and normalize them into a Polars DataFrame | Type decisions, cleaning, validation verdicts |
| `profiling/` | Compute factual dataset and column statistics | Decide how to repair data |
| `inference/` | Infer physical type, semantic type, column role, and confidence | Mutate source data |
| `validation/` | Apply quality rules and produce issues | Perform automatic fixes in Phase 1 |
| `orchestration/` | Run modules in the correct order and manage run state | Implement business logic |
| `reporting/` | Convert outputs into stable JSON/API responses | Recompute data statistics |
| `domain/` | Shared typed models, enums, and contracts | File reading or API logic |
| `storage/` | Persist source/staged datasets and reports | Run pipeline logic |

The core pipeline should remain deliberately simple:

text

Upload file
 ↓
Ingest and normalize
 ↓
Generate factual profile
 ↓
Infer schema and roles
 ↓
Run validation rules
 ↓
Create report JSON
 ↓
Store staged Parquet + report

## Core Domain Models

Keep these files as Pydantic models from the beginning. They become the stable contract between your frontend, API, storage, and future modules.

## `domain/enums.py`

python

from enum import Enum

class PhysicalType(str, Enum):
 INTEGER = "integer"
 FLOAT = "float"
 BOOLEAN = "boolean"
 STRING = "string"
 DATETIME = "datetime"
 UNKNOWN = "unknown"

class SemanticType(str, Enum):
 NUMERIC = "numeric"
 CATEGORICAL = "categorical"
 DATETIME = "datetime"
 TEXT = "text"
 IDENTIFIER = "identifier"
 EMAIL = "email"
 PHONE = "phone"
 URL = "url"
 BOOLEAN = "boolean"
 UNKNOWN = "unknown"

class ColumnRole(str, Enum):
 FEATURE = "feature"
 TARGET_CANDIDATE = "target_candidate"
 IDENTIFIER = "identifier"
 DATETIME = "datetime"
 IGNORE = "ignore"

class Severity(str, Enum):
 INFO = "info"
 WARNING = "warning"
 ERROR = "error"

class IssueCode(str, Enum):
 HIGH_NULL_RATE = "high_null_rate"
 DUPLICATE_ROWS = "duplicate_rows"
 CONSTANT_COLUMN = "constant_column"
 MIXED_TYPE = "mixed_type"
 HIGH_CARDINALITY = "high_cardinality"
 INVALID_DATETIME = "invalid_datetime"
 SUSPICIOUS_IDENTIFIER = "suspicious_identifier"

## `domain/models/column.py`

python

from pydantic import BaseModel, Field
from platform_core.domain.enums import PhysicalType, SemanticType, ColumnRole

class TypeCandidate(BaseModel):
 type: str
 confidence: float = Field(ge=0.0, le=1.0)
 evidence: list[str] = []

class ColumnProfile(BaseModel):
 name: str
 position: int
 physical_type: PhysicalType
 semantic_type: SemanticType
 role: ColumnRole

 total_count: int
 non_null_count: int
 null_count: int
 null_percentage: float

 unique_count: int
 unique_percentage: float
 sample_values: list[str | int | float | bool | None] = []

 inferred_type_confidence: float
 alternative_type_candidates: list[TypeCandidate] = []

 numeric_min: float | None = None
 numeric_max: float | None = None
 numeric_mean: float | None = None
 numeric_median: float | None = None

 most_common_values: list[dict] = []
 detected_formats: list[str] = []

## `domain/models/validation.py`

python

from pydantic import BaseModel
from platform_core.domain.enums import Severity, IssueCode

class ValidationIssue(BaseModel):
 code: IssueCode
 severity: Severity
 title: str
 message: str

 column_name: str | None = None
 affected_rows: int | None = None
 affected_percentage: float | None = None

 evidence: dict = {}
 recommended_action: str | None = None
 auto_fix_available: bool = False

## `domain/models/profile.py`

python

from pydantic import BaseModel
from platform_core.domain.models.column import ColumnProfile
from platform_core.domain.models.validation import ValidationIssue

class DatasetProfile(BaseModel):
 dataset_id: str
 file_name: str
 file_format: str
 created_at: str

 row_count: int
 column_count: int
 duplicate_row_count: int
 memory_usage_bytes: int

 columns: list[ColumnProfile]
 validation_issues: list[ValidationIssue]

 quality_score: float
 summary: dict

## Stable Report Contract

Every Phase 1 pipeline run should produce one report in this shape:

json

{
 "dataset_id": "ds_01JX9R4B7ZK",
 "file_name": "customer_churn.csv",
 "file_format": "csv",
 "created_at": "2026-07-28T14:30:00Z",

 "dataset": {
 "row_count": 10000,
 "column_count": 18,
 "duplicate_row_count": 42,
 "memory_usage_bytes": 1843200,
 "staged_dataset_path": "data/staging/ds_01JX9R4B7ZK.parquet"
 },

 "columns": [
 {
 "name": "customer_id",
 "position": 0,
 "physical_type": "string",
 "semantic_type": "identifier",
 "role": "identifier",
 "inferred_type_confidence": 0.99,

 "total_count": 10000,
 "non_null_count": 10000,
 "null_count": 0,
 "null_percentage": 0.0,

 "unique_count": 10000,
 "unique_percentage": 100.0,
 "sample_values": ["CUS-001", "CUS-002", "CUS-003"],

 "alternative_type_candidates": [
 {
 "type": "categorical",
 "confidence": 0.2,
 "evidence": ["Values are short strings"]
 }
 ],

 "most_common_values": [],
 "detected_formats": ["CUS-{integer}"]
 }
 ],

 "validation": {
 "issue_count": 4,
 "error_count": 1,
 "warning_count": 3,
 "info_count": 0,
 "issues": [
 {
 "code": "high_null_rate",
 "severity": "warning",
 "title": "High missing-value rate",
 "message": "Column 'monthly_charges' is 18.4% missing.",
 "column_name": "monthly_charges",
 "affected_rows": 1840,
 "affected_percentage": 18.4,
 "evidence": {
 "null_count": 1840,
 "threshold": 10.0
 },
 "recommended_action": "Evaluate median imputation or remove the column if missingness is not informative.",
 "auto_fix_available": false
 }
 ]
 },

 "quality_score": 82.5,
 "summary": {
 "numeric_columns": 6,
 "categorical_columns": 7,
 "datetime_columns": 2,
 "identifier_columns": 1,
 "target_candidates": ["churn"],
 "recommended_next_step": "Review validation warnings before running automated cleaning."
 }
}

Do not rename fields casually after this. Version the contract instead when a breaking change becomes necessary:

json

{
 "schema_version": "1.0",
 "dataset_id": "ds_01JX9R4B7ZK"
}

## First API Endpoints

Keep the API intentionally small in Phase 1:

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Verify API and storage availability |
| `POST /v1/datasets/upload` | Upload CSV, Excel, JSON, or Parquet file |
| `POST /v1/datasets/{dataset_id}/analyze` | Trigger ingest → profile → infer → validate |
| `GET /v1/datasets/{dataset_id}` | Get dataset metadata and current status |
| `GET /v1/datasets/{dataset_id}/report` | Return the completed Phase 1 report |
| `GET /v1/datasets/{dataset_id}/preview` | Return a safe sample of rows |
| `DELETE /v1/datasets/{dataset_id}` | Delete uploaded file, staged data, and report |

For the first working version, `POST /upload` can automatically start analysis. Split it into async jobs later, when your UI and large-file requirements justify it.

## Build Order

## Day 1: Project Skeleton

Create the repository, Python environment, FastAPI app, health endpoint, settings management, Git hooks, and test setup.

bash

uv init auto-data-platform
cd auto-data-platform

uv add fastapi "uvicorn[standard]" polars pyarrow pydantic pydantic-settings
uv add python-multipart charset-normalizer openpyxl
uv add --dev pytest pytest-cov ruff mypy

## Day 2–3: CSV Ingestion

Implement `csv_reader.py`, encoding detection, delimiter detection, header handling, basic upload endpoint, local storage, and CSV fixtures.

**Definition of done:** upload a messy CSV, stage it as Parquet, preview its first 100 rows, and return its dataset ID.

## Day 4–5: Profiling

Implement row count, null metrics, unique counts, duplicates, top values, numerical statistics, and column samples.

**Definition of done:** a `DatasetProfile` JSON object is generated from staged Parquet.

## Day 6–8: Type and Role Inference

Start with only these semantic types:

- Numeric
- Categorical
- Datetime
- Boolean
- Text
- Identifier
- Unknown

Then infer roles: feature, identifier, datetime, target candidate, ignore. Do not try to perfectly infer targets; label candidates and require user confirmation.

## Day 9–10: Validation

Implement only four rules first:

- High null rate
- Duplicate rows
- Constant columns
- Mixed-type columns

Each rule must return `ValidationIssue`, never modify the DataFrame. Cleaning belongs to Phase 2.

## Day 11–12: Reporting and Integration

Connect the full pipeline through `orchestration/pipeline.py`, write JSON reports, expose report endpoint, and create end-to-end integration tests.

## Essential Tests

Your minimum initial fixture set should cover:

| Fixture | What it proves |
| --- | --- |
| `clean_sales.csv` | Normal happy-path ingest and profiling |
| `dirty_sales.csv` | Nulls, inconsistent categories, blank values |
| `mixed_types.csv` | Numbers and strings mixed in one column |
| `duplicate_rows.csv` | Exact duplicate detection |
| `broken_dates.csv` | Invalid and mixed date formats |
| `high_cardinality.csv` | Identifier-like fields and cardinality logic |
| `utf16_semicolon.csv` | Encoding and delimiter detection |
| `customer_data.xlsx` | Excel sheet ingestion |
| `events.parquet` | Parquet path works without conversion issues |

## Cursor Prompt: Initial Scaffold

text

Create a production-quality Python 3.11 project using src layout named
"platform_core" for an automated data cleaning, preprocessing, and feature
engineering platform.

Phase 1 scope only:

- FastAPI API
- CSV, Excel, and Parquet ingestion
- Polars as the internal DataFrame engine
- Dataset profiling
- Type inference
- Validation reporting

Create the reduced folder structure specified below. Use Pydantic v2 models,
Ruff, pytest, type hints, custom domain exceptions, and dependency injection
where useful. Do not implement data cleaning, feature engineering, model
training, authentication, database persistence, or frontend code.

The core pipeline is:
ingest -> stage as Parquet -> profile -> infer schema -> validate -> JSON report.

Every module must have focused unit tests. Generate a README with run and test
commands. Do not use global mutable state.

## Antigravity Prompt: CSV Reader

text

Implement `src/platform_core/ingestion/readers/csv_reader.py` for a Python 3.11
FastAPI/Polars application.

Requirements:

- Accept a file path and return a Polars DataFrame plus ingestion metadata.
- Detect probable text encoding using charset-normalizer.
- Detect delimiter among comma, semicolon, tab, and pipe.
- Support quoted values, empty strings, malformed rows, and UTF-8 BOM.
- Preserve initial raw column names; do not clean or rename them.
- Capture metadata: encoding, delimiter, headers detected, source row count,
 source column count, warnings.
- Raise typed domain exceptions with actionable messages.
- Write unit tests for UTF-8 CSV, UTF-16 CSV, semicolon CSV, tab CSV,
 malformed rows, blank header names, BOM, quoted delimiters, and empty file.
- Do not build API endpoints or schema inference.

## Architecture Rule

Phase 1 should only **observe, classify, validate, and report**. It must not silently clean, drop, encode, impute, scale, generate features, or select a target. Those transformations belong to later platform phases, while the Phase 1 report becomes their trusted input contract.

Prepared using Kimi K3

Ask a follow-up

SearchComputer

Kimi K3 Thinking

![](https://edge.perplexity.ai/image)
