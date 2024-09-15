from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel


# Enum for input types
class InputTypeKey(StrEnum):
    TARGET_FOLDER = "TARGET_FOLDER"
    KNOWN_DATASET = "KNOWN_DATASET"
    KNOWN_DATASET_SQL = "KNOWN_DATASET_SQL"
    OUTPUT_FOLDER = "OUTPUT_FOLDER"


# Model for individual input
class _Input(BaseModel):
    input_type: InputTypeKey
    file_path: str


# Model for parameters
class _Parameters(BaseModel):
    block_size: int
    target_probability: float


# Model for request
class ModelRequest(BaseModel):
    data_type: str
    inputs: List[_Input]
    parameters: _Parameters

    @classmethod
    def validate_files(cls, result):
        input_keys = [inp.input_type for inp in result.inputs]
        if InputTypeKey.KNOWN_DATASET in input_keys and InputTypeKey.KNOWN_DATASET_SQL in input_keys:
            raise ValueError("Both known_dataset path and known_dataset_sql path cannot be provided.")
        return result


# Model for result
class ModelResponse(BaseModel):
    found: bool
    target_file: Optional[str] = None
    known_dataset_file: Optional[str] = None

    # Additional validation to ensure files are provided if found is True
    @classmethod
    def validate_files(cls, result):
        if result.found and (not result.target_file or not result.known_dataset_file):
            raise ValueError("Both target_file and known_dataset_file must be provided if found is True.")
        return result
