"""Dataframe utilities."""
from typing import Any

import polars as pl


def get_row_count(df: pl.DataFrame) -> int:
    """Get the number of rows in a dataframe.
    
    Args:
        df: Polars dataframe
        
    Returns:
        Row count
    """
    return df.height

def to_pandas(df: pl.DataFrame) -> Any:
    """Convert Polars DataFrame to Pandas DataFrame at the boundary.
    
    Args:
        df: Polars dataframe
        
    Returns:
        Pandas dataframe
    """
    return df.to_pandas()

