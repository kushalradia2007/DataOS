from pathlib import Path

import polars as pl

from platform_core.domain.enums import ColumnRole, SemanticType
from platform_core.inference.role_inference import infer_column_role
from platform_core.inference.type_inference import infer_semantic_type


def test_inference():
    fixtures_dir = Path("tests/fixtures")
    
    # Let's define the expected values
    expected = {
        "dirty_sales.csv": {
            "id": (SemanticType.IDENTIFIER, ColumnRole.IDENTIFIER),
            "sales": (SemanticType.NUMERIC, ColumnRole.TARGET_CANDIDATE),
            "category": (SemanticType.CATEGORICAL, ColumnRole.FEATURE)
        },
        "mixed_types.csv": {
            "a": (SemanticType.IDENTIFIER, ColumnRole.IDENTIFIER), # 1, 2, 3
            "b": (SemanticType.IDENTIFIER, ColumnRole.IDENTIFIER), # x, y, z -> could be id or cat
            "c": (SemanticType.BOOLEAN, ColumnRole.FEATURE) # true, false, null
        },
        "utf8.csv": {
            "col1": (SemanticType.IDENTIFIER, ColumnRole.IDENTIFIER), # 1, 3
            "col2": (SemanticType.IDENTIFIER, ColumnRole.IDENTIFIER), # añejo, 4
        }
    }
    
    correct = 0
    total = 0
    
    for filename, expected_cols in expected.items():
        filepath = fixtures_dir / filename
        if not filepath.exists():
            continue
            
        df = pl.read_csv(filepath, infer_schema_length=0) # Read all as string to test heuristics? Wait, no, let polars infer
        df = pl.read_csv(filepath)
        
        # Calculate exact_stats similar to profiling service
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
        
        print(f"\n--- {filename} ---")
        for col in df.columns:
            if col not in expected_cols:
                continue
                
            total += 2 # type and role
            
            exp_type, exp_role = expected_cols[col]
            
            sem_type, conf, evidence, cands = infer_semantic_type(df[col], exact_stats)
            role, r_evidence = infer_column_role(sem_type, col)
            
            type_match = sem_type == exp_type
            if type_match:
                correct += 1
            else:
                print(f"[X] {col} Type: expected {exp_type}, got {sem_type} (conf={conf:.2f})")
                print(f"    Evidence: {evidence}")
                print(f"    Candidates: {[f'{c.type}({c.confidence:.2f})' for c in cands]}")
                
            role_match = role == exp_role
            if role_match:
                correct += 1
            else:
                print(f"[X] {col} Role: expected {exp_role}, got {role}")
                print(f"    Evidence: {r_evidence}")
                
            if type_match and role_match:
                print(f"[OK] {col}: {sem_type.value} ({conf:.2f}), {role.value}")
                
    if total > 0:
        acc = correct / total
        print(f"\nAccuracy: {acc:.1%} ({correct}/{total})")
    else:
        print("No tests matched.")

if __name__ == "__main__":
    test_inference()
