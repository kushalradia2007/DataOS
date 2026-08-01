"""ID generation utilities."""
import re
import uuid


def generate_id(prefix: str) -> str:
    """Generate a unique identifier.
    
    Args:
        prefix: Prefix for the ID
        
    Returns:
        Generated unique ID
    """
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def generate_dataset_id() -> str:
    """Generate a dataset ID."""
    return generate_id("ds")

DATASET_ID_REGEX = re.compile(r"^ds_[0-9a-f]{8}$")

def validate_dataset_id(dataset_id: str) -> bool:
    """Validate that a dataset ID strictly matches the generated format."""
    return bool(DATASET_ID_REGEX.match(dataset_id))
