"""Orchestration pipeline."""
import json
from pathlib import Path
from typing import Any

from platform_core.domain.enums import Severity
from platform_core.inference.role_inference import infer_column_role
from platform_core.inference.type_inference import infer_semantic_type
from platform_core.ingestion.readers.base import BaseReader
from platform_core.ingestion.readers.csv_reader import CSVReader
from platform_core.ingestion.readers.excel_reader import ExcelReader
from platform_core.ingestion.readers.parquet_reader import ParquetReader
from platform_core.ingestion.staging import stage_dataset
from platform_core.profiling.service import ProfilingService
from platform_core.shared.exceptions import UnsupportedFormatError
from platform_core.validation.rules import (
    ConstantColumnRule,
    DuplicateRowsRule,
    HighNullRateRule,
    MixedTypeRule,
)


def run_pipeline(file_path: Path, output_dir: Path = Path("data/reports"), original_file_name: str | None = None) -> dict[str, Any]:
    """Run the synchronous processing pipeline."""
    # 1. Ingest
    suffix = file_path.suffix.lower()
    reader: BaseReader
    if suffix == ".csv":
        reader = CSVReader()
    elif suffix in {".xlsx", ".xls"}:
        reader = ExcelReader()
    elif suffix == ".parquet":
        reader = ParquetReader()
    else:
        raise UnsupportedFormatError(f"Unsupported format: {suffix}")
        
    df, _metadata = reader.read(file_path)
    
    # 2. Stage
    staging_result = stage_dataset(df, file_path)
    dataset_id = staging_result.dataset_id
    
    # 3. Profile
    profiling_service = ProfilingService(reports_dir=output_dir)
    profile = profiling_service.profile(df, dataset_id)
    if original_file_name:
        profile.file_name = original_file_name
    
    # Exact stats for inference
    exact_stats = {
        "row_count": df.height,
        "columns": {
            col: {
                "null_count": df[col].null_count(),
                "n_unique": df[col].n_unique(),
            }
            for col in df.columns
        }
    }
    
    # 4. Infer
    for col_profile in profile.columns:
        col_name = col_profile.name
        
        # Semantic Type Inference
        semantic_type, confidence, _evidence, candidates = infer_semantic_type(df[col_name], exact_stats)
        
        # Role Inference
        role, _role_evidence = infer_column_role(semantic_type, col_name)
        
        # Update column profile
        col_profile.semantic_type = semantic_type
        col_profile.inferred_type_confidence = confidence
        col_profile.alternative_type_candidates = candidates
        col_profile.role = role
        
    # 5. Validate
    rules = [
        HighNullRateRule(),
        DuplicateRowsRule(exact_duplicate_count=profile.duplicate_row_count),
        ConstantColumnRule(),
        MixedTypeRule(),
    ]
    
    validation_issues = []
    for rule in rules:
        validation_issues.extend(rule.evaluate(df))
        
    profile.validation_issues = validation_issues
    
    # Update quality score
    score = 100.0
    for issue in validation_issues:
        if issue.severity == Severity.ERROR:
            score -= 10
        elif issue.severity == Severity.WARNING:
            score -= 5
    profile.quality_score = max(0.0, score)
    
    # 6. Report
    report_dict = profile.model_dump(mode="json")
    
    # Save report locally
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{dataset_id}.json"
    report_path.write_text(json.dumps(report_dict, indent=2), encoding="utf-8")
    
    return report_dict
