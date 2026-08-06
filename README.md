# Auto Data Platform Phase 1

An AI-powered ML Data Preparation Platform that understands datasets, recommends an explainable preprocessing pipeline, lets users modify every decision through an interactive visual pipeline builder, produces ML-ready datasets, and generates an intelligent ML Readiness Report with actionable guidance for the next steps.

## Features
- **Multi-format Ingestion**: Load CSV, Excel, and Parquet files safely.
- **Intelligent Schema Detection**: Auto-infer columns (numeric, categorical, datetime, text, ID) with confidence scores.
- **In-depth Profiling**: Generate summary statistics and clean interactive HTML profile reports.
- **Robust Data Validation**: Detect null rates, duplicate rows, constant columns, and mixed data types.
- **FastAPI API**: Upload datasets, fetch validation metrics, and view generated reports via clean API endpoints.

---

## Getting Started

### Prerequisites
- Python 3.11 or higher
- `uv` (recommended fast package installer) or standard `pip`

---

### Setup & Installation

#### Option 1: Using `uv` (Recommended)
1. Install [uv](https://github.com/astral-sh/uv) if you haven't already.
2. Sync the virtual environment and install dependencies:
   ```bash
   uv sync
   ```
3. Activate the virtual environment:
   - **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
   - **Windows (CMD):** `.venv\Scripts\activate.bat`
   - **macOS/Linux:** `source .venv/bin/activate`

#### Option 2: Using `pip`
1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate it:
   - **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`
   - **macOS/Linux:** `source .venv/bin/activate`
3. Install the package and dependencies:
   ```bash
   pip install -e .
   ```

---

## Running the Application

### 1. Start the API Server
Run the FastAPI development server:
```bash
python -m uvicorn platform_core.api.app:app --reload
```
Once running, you can open:
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **API Healthcheck:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

### 2. Run the Verification Tests
We have a comprehensive test suite covering ingestion, inference, profiling, validation rules, and the API.

To run all tests:
```bash
python -m pytest tests/ -v
```

To run with coverage reporting:
```bash
python -m pytest tests/ --cov=src
```

---

## Project Structure
- `src/platform_core/` - Core module implementation.
  - `api/` - FastAPI application, routes, and endpoints.
  - `domain/` - Pydantic schemas and domain models (Dataset, Profiles, Validation issues).
  - `ingestion/` - Readers (CSV, Parquet, Excel) and staging logic.
  - `inference/` - Type & role inference logic.
  - `profiling/` - Profile mapping and HTML report generation.
  - `validation/` - Validation rules engine.
- `tests/` - Unit and integration tests.
- `scripts/` - Utilities for generating test fixtures and running inference verification.

