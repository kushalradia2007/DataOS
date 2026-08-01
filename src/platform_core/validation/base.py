"""Validation rule engine base classes."""
from abc import ABC, abstractmethod

import polars as pl

from platform_core.domain.models.validation import ValidationIssue


class ValidationRule(ABC):
    """Abstract base class for all validation rules."""
    
    @abstractmethod
    def evaluate(self, df: pl.DataFrame) -> list[ValidationIssue]:
        """Evaluate the rule against a dataframe and return any validation issues.
        
        Args:
            df: The Polars DataFrame to validate.
            
        Returns:
            A list of ValidationIssue objects. Empty list if no issues are found.
        """
