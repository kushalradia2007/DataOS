"""Dataset models."""
from pydantic import BaseModel


class Dataset(BaseModel):
    """Represents a dataset entity."""
    dataset_id: str
    file_name: str
    file_format: str
    staged_dataset_path: str | None = None
