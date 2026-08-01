"""Role inference heuristics."""
from platform_core.domain.enums import ColumnRole, SemanticType


def infer_column_role(
    semantic_type: SemanticType, col_name: str
) -> tuple[ColumnRole, list[str]]:
    """Infer the role of a column based on heuristics."""
    evidence = []
    
    # 1. Identifier (by name)
    id_words = {"id", "uuid", "guid", "pk"}
    if col_name.lower() in id_words or col_name.lower().endswith("_id"):
        evidence.append(f"Column name '{col_name}' strongly implies identifier.")
        return ColumnRole.IDENTIFIER, evidence
        
    # 2. Target heuristic
    target_words = {"target", "label", "y", "is_churn", "sales", "fraud"}
    if col_name.lower() in target_words:
        evidence.append(f"Column name '{col_name}' matches known target synonyms.")
        return ColumnRole.TARGET_CANDIDATE, evidence
        
    # 3. Identifier (by type)
    if semantic_type == SemanticType.IDENTIFIER:
        evidence.append("Semantic type is identifier.")
        return ColumnRole.IDENTIFIER, evidence
        
    # 3. Datetime
    if semantic_type == SemanticType.DATETIME:
        evidence.append("Semantic type is datetime.")
        return ColumnRole.DATETIME, evidence
        
    # 4. Feature fallback
    evidence.append(f"Defaulting to feature for semantic type '{semantic_type.value}'.")
    return ColumnRole.FEATURE, evidence
