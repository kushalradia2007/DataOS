"""Type inference heuristics."""
import polars as pl

from platform_core.domain.enums import SemanticType
from platform_core.domain.models.column import TypeCandidate
from platform_core.inference.confidence import (
    create_candidate,
    evaluate_boolean_confidence,
    evaluate_categorical_confidence,
    evaluate_identifier_confidence,
)

# Replacement for deprecated pl.NUMERIC_DTYPES
_NUMERIC_DTYPES: frozenset[type[pl.DataType]] = frozenset({
    pl.Int8, pl.Int16, pl.Int32, pl.Int64,
    pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
    pl.Float32, pl.Float64,
})


def infer_semantic_type(
    series: pl.Series, exact_stats: dict[str, object]
) -> tuple[SemanticType, float, list[str], list[TypeCandidate]]:
    """Infer the semantic type of a column based on heuristics."""
    candidates: list[TypeCandidate] = []
    
    col_name = series.name
    col_stats_raw = exact_stats["columns"]
    assert isinstance(col_stats_raw, dict)
    col_stats = col_stats_raw[col_name]
    assert isinstance(col_stats, dict)
    null_count_val = col_stats["null_count"]
    assert isinstance(null_count_val, int)
    null_count: int = null_count_val
    total_count_val = exact_stats["row_count"]
    assert isinstance(total_count_val, int)
    total_count: int = total_count_val
    non_null_count = total_count - null_count
    n_unique_raw_val = col_stats["n_unique"]
    assert isinstance(n_unique_raw_val, int)
    n_unique_raw: int = n_unique_raw_val
    # Polars n_unique includes null if present. For cardinality/uniqueness of values, subtract 1 if nulls exist
    n_unique = n_unique_raw - 1 if null_count > 0 else n_unique_raw
    dtype = series.dtype
    
    # 1. Evaluate Categorical
    cat_cand = evaluate_categorical_confidence(n_unique, non_null_count, total_count)
    if cat_cand.confidence > 0:
        candidates.append(cat_cand)
        
    # 2. Evaluate Identifier
    id_cand = evaluate_identifier_confidence(n_unique, non_null_count, total_count)
    id_words = {"id", "uuid", "guid", "pk"}
    if col_name.lower() in id_words or col_name.lower().endswith("_id"):
        id_cand.confidence = max(id_cand.confidence, 0.9)
        if f"Column name '{col_name}' suggests identifier" not in id_cand.evidence:
            id_cand.evidence.append(f"Column name '{col_name}' suggests identifier")
    if id_cand.confidence > 0:
        candidates.append(id_cand)
        
    # 3. Evaluate Boolean
    bool_cand = evaluate_boolean_confidence(series, non_null_count)
    if bool_cand.confidence > 0:
        candidates.append(bool_cand)
        
    # 4. Evaluate Numeric
    num_evidence: list[str] = []
    num_conf = 0.0
    if type(dtype) in _NUMERIC_DTYPES:
        num_conf = 0.85
        num_evidence.append(f"Polars dtype is {dtype}")
    elif dtype in (pl.String, pl.Utf8) and non_null_count > 0:
        s_not_null = series.drop_nulls()
        # strict=False cast
        try:
            parsed = s_not_null.cast(pl.Float64, strict=False)
            parsed_count = parsed.drop_nulls().len()
            parse_rate = parsed_count / non_null_count
            if parse_rate > 0.8:
                num_conf = parse_rate
                num_evidence.append(f"Float parse rate is {parse_rate:.2f}")
        except (ValueError, TypeError, pl.exceptions.ComputeError):
            pass  # Column cannot be parsed as numeric
            
    if num_conf > 0:
        candidates.append(create_candidate(SemanticType.NUMERIC, num_conf, num_evidence))
        
    # 5. Evaluate Datetime
    dt_evidence: list[str] = []
    dt_conf = 0.0
    if dtype in (pl.Datetime, pl.Date, pl.Time):
        dt_conf = 0.95
        dt_evidence.append(f"Polars dtype is {dtype}")
    elif dtype in (pl.String, pl.Utf8) and non_null_count > 0:
        s_not_null = series.drop_nulls()
        try:
            parsed = s_not_null.str.to_datetime(strict=False)
            parsed_count = parsed.drop_nulls().len()
            parse_rate = parsed_count / non_null_count
            if parse_rate > 0.8:
                dt_conf = parse_rate
                dt_evidence.append(f"Datetime parse rate is {parse_rate:.2f}")
        except (ValueError, TypeError, pl.exceptions.ComputeError):
            pass  # Column cannot be parsed as datetime
            
    if dt_conf > 0:
        candidates.append(create_candidate(SemanticType.DATETIME, dt_conf, dt_evidence))
        
    # 6. Evaluate Text
    text_evidence: list[str] = []
    text_conf = 0.0
    if dtype in (pl.String, pl.Utf8) and non_null_count > 0:
        s_not_null = series.drop_nulls()
        avg_len = s_not_null.str.len_chars().mean()
        if avg_len is not None and isinstance(avg_len, (int, float)) and avg_len > 30:
            text_conf = 0.7
            text_evidence.append(f"Average string length ({avg_len:.1f}) > 30")
        else:
            text_conf = 0.3
            avg_len_display = f"{avg_len:.1f}" if isinstance(avg_len, (int, float)) else "N/A"
            text_evidence.append(f"Polars dtype is {dtype} with length <= 30 (avg={avg_len_display})")
    if text_conf > 0:
        candidates.append(create_candidate(SemanticType.TEXT, text_conf, text_evidence))
        
    # Fallback to UNKNOWN if no candidates
    if not candidates:
        candidates.append(create_candidate(SemanticType.UNKNOWN, 1.0, ["No patterns matched"]))
        
    # Boosts to resolve conflicts
    for c in candidates:
        if c.type == SemanticType.BOOLEAN.value and c.confidence >= 0.9:
            c.confidence += 0.2  # boolean beats numeric 0/1
        if c.type == SemanticType.IDENTIFIER.value and c.confidence >= 0.9:
            c.confidence += 0.1  # identifier beats numeric for IDs
            
    # Sort candidates by confidence descending
    candidates.sort(key=lambda c: c.confidence, reverse=True)
    
    # Ensure confidence is clamped
    for c in candidates:
        c.confidence = max(0.0, min(1.0, c.confidence))
        
    best_candidate = candidates[0]
    
    semantic_type = SemanticType(best_candidate.type)
    
    return semantic_type, best_candidate.confidence, best_candidate.evidence, candidates
