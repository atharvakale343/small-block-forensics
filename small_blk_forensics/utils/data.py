from typing import Optional, TypedDict

from pydantic import BaseModel


class Parameters(TypedDict):
    block_size: int
    target_probability: float


# Model for result
class MyModelResponse(BaseModel):
    found: bool
    target_file: Optional[str] = None
    known_dataset_file: Optional[str] = None
    block_num_in_known_dataset: Optional[int] = None
    block_num_in_target: Optional[int] = None

    # Additional validation to ensure files are provided if found is True
    @classmethod
    def validate_files(cls, result):
        if result.found and (not result.target_file or not result.known_dataset_file):
            raise ValueError("Both target_file and known_dataset_file must be provided if found is True.")
        return result
