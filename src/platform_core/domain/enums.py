"""Domain enums."""
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
