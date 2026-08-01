"""Confidence heuristics for type inference."""
from __future__ import annotations

import polars as pl

from platform_core.domain.enums import SemanticType
from platform_core.domain.models.column import TypeCandidate


def create_candidate(semantic_type: SemanticType, confidence: float, evidence: list[str]) -> TypeCandidate:
    """Create a TypeCandidate with constrained confidence [0, 1]."""
    confidence = max(0.0, min(1.0, confidence))
    return TypeCandidate(type=semantic_type.value, confidence=confidence, evidence=evidence)

def evaluate_categorical_confidence(n_unique: int, non_null_count: int, total_count: int) -> TypeCandidate:
    """Evaluate confidence for categorical type based on cardinality."""
    evidence: list[str] = []
    confidence = 0.0
    
    if non_null_count == 0:
        return create_candidate(SemanticType.CATEGORICAL, 0.0, ["No non-null values"])
        
    cardinality_ratio = n_unique / non_null_count
    
    if n_unique <= 20 and n_unique > 0:
        confidence += 0.8
        evidence.append(f"Low absolute cardinality ({n_unique} <= 20)")
    elif cardinality_ratio < 0.1:
        confidence += 0.6
        evidence.append(f"Low cardinality ratio ({cardinality_ratio:.2f} < 0.1)")
    
    return create_candidate(SemanticType.CATEGORICAL, confidence, evidence)

def evaluate_identifier_confidence(n_unique: int, non_null_count: int, total_count: int) -> TypeCandidate:
    """Evaluate confidence for identifier type based on uniqueness."""
    evidence: list[str] = []
    confidence = 0.0
    
    if non_null_count == 0:
        return create_candidate(SemanticType.IDENTIFIER, 0.0, ["No non-null values"])
        
    uniqueness_ratio = n_unique / non_null_count
    
    if uniqueness_ratio >= 0.95:
        confidence += 0.9
        evidence.append(f"High uniqueness ratio ({uniqueness_ratio:.2f} >= 0.95)")
    
    return create_candidate(SemanticType.IDENTIFIER, confidence, evidence)

def evaluate_boolean_confidence(series: pl.Series, non_null_count: int) -> TypeCandidate:
    """Evaluate confidence for boolean type based on string values."""
    evidence: list[str] = []
    confidence = 0.0
    
    if non_null_count == 0:
        return create_candidate(SemanticType.BOOLEAN, 0.0, ["No non-null values"])
        
    if series.dtype == pl.Boolean:
        return create_candidate(SemanticType.BOOLEAN, 1.0, ["Polars dtype is Boolean"])
        
    if series.dtype in (pl.String, pl.Utf8):
        # Check subset of true/false values
        bool_strings = {"true", "false", "t", "f", "yes", "no", "y", "n", "1", "0"}
        unique_vals = series.drop_nulls().unique().str.to_lowercase().to_list()
        
        is_subset = all(str(v) in bool_strings for v in unique_vals if v is not None)
        if is_subset and len(unique_vals) > 0:
            confidence = 0.9
            evidence.append(f"Values are a subset of known booleans: {unique_vals}")
            
    return create_candidate(SemanticType.BOOLEAN, confidence, evidence)
