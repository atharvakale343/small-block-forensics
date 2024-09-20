from enum import StrEnum
from typing import List, Optional

from flask_ml.flask_ml_server.models import CustomInput
from pydantic import BaseModel


# Enum for input types
class InputTypeKey(StrEnum):
    TARGET_FOLDER = "TARGET_FOLDER"
    KNOWN_DATASET = "KNOWN_DATASET"
    INPUT_SQL = "INPUT_SQL"
    OUTPUT_SQL_PATH = "OUTPUT_SQL_PATH"


# Model for individual input
class _Input(BaseModel):
    input_type: InputTypeKey
    file_path: str


# Model for parameters
class _Parameters(BaseModel):
    block_size: int
    target_probability: float


# Model for request
class MyModelRequest(BaseModel):
    data_type: str
    inputs: List[CustomInput]
    parameters: _Parameters

    @classmethod
    def validate_files(cls, result):
        input_keys = [inp.input_type for inp in result.inputs]
        if InputTypeKey.KNOWN_DATASET in input_keys and InputTypeKey.INPUT_SQL in input_keys:
            raise ValueError("Both known_dataset path and known_dataset_sql path cannot be provided.")
        return result


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
