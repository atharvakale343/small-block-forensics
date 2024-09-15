from pathlib import Path

from flask_ml.flask_ml_server import MLServer  # type: ignore
from flask_ml.flask_ml_server.constants import DataTypes  # type: ignore
from flask_ml.flask_ml_server.response import (  # type: ignore
    ErrorResponse,
    TextResponse,
)
from pydantic import ValidationError

from small_blk_forensics.utils.common import is_dir_path
from small_blk_forensics.utils.data import InputTypeKey, ModelRequest

from ..ml.model import SmallBlockForensicsModel

model = SmallBlockForensicsModel()
server = MLServer(__name__)


@server.route("/execute", input_type=DataTypes.TEXT)
def execute(inputs: list[dict], parameters: dict):
    print("Inputs:", inputs)
    print("Parameters:", parameters)
    try:
        model_request = ModelRequest(data_type=DataTypes.TEXT, inputs=inputs, parameters=parameters)  # type: ignore
    except ValidationError as e:
        return ErrorResponse(message=str(e), status=400).get_response()

    target_directory, known_content_directory, existing_known_content_db, output_directory = (
        None,
        None,
        None,
        None,
    )
    for inp in model_request.inputs:
        if inp.input_type == InputTypeKey.TARGET_FOLDER.value:
            target_directory = inp.file_path
        if inp.input_type == InputTypeKey.KNOWN_DATASET.value:
            known_content_directory = inp.file_path
        if inp.input_type == InputTypeKey.KNOWN_DATASET_SQL.value:
            existing_known_content_db = inp.file_path
        if inp.input_type == InputTypeKey.OUTPUT_FOLDER.value:
            output_directory = inp.file_path

    if target_directory is None or not is_dir_path(target_directory):
        return ErrorResponse(
            f"{InputTypeKey.TARGET_FOLDER.value} {target_directory} is not provided or is not a valid path",
            status=400,
        ).get_response()
    target_directory_path = Path(target_directory)
    del target_directory

    if output_directory is None or not is_dir_path(output_directory):
        return ErrorResponse(
            f"{InputTypeKey.OUTPUT_FOLDER.value} {output_directory} is not provided or is not a valid path",
            status=400,
        ).get_response()
    output_directory_path = Path(output_directory)
    del output_directory

    if not (known_content_directory or existing_known_content_db):
        return ErrorResponse(
            f"Either {InputTypeKey.KNOWN_DATASET.value} or {InputTypeKey.KNOWN_DATASET_SQL.value} must be specified",
            status=400,
        ).get_response()

    if known_content_directory and existing_known_content_db:
        return ErrorResponse(
            f"Both {InputTypeKey.KNOWN_DATASET.value} and {InputTypeKey.KNOWN_DATASET_SQL.value} cannot be specified",
            status=400,
        ).get_response()

    if known_content_directory:
        if not is_dir_path(known_content_directory):
            return ErrorResponse(f"{known_content_directory} is not a valid path", status=400).get_response()
        known_content_directory_path = Path(known_content_directory)
        del known_content_directory

        return TextResponse(
            model.run_with_known_content_directory(
                known_content_directory_path, target_directory_path, output_directory_path
            ).model_dump(exclude_none=True)
        ).get_response()
    else:
        if existing_known_content_db is None or not is_dir_path(existing_known_content_db):
            return ErrorResponse(
                f"{existing_known_content_db} is not a valid path", status=400
            ).get_response()
        existing_known_content_db_path = Path(existing_known_content_db)
        del existing_known_content_db

        return TextResponse(
            model.run_with_known_content_sqlite(
                existing_known_content_db_path, target_directory_path, output_directory_path
            ).model_dump(exclude_none=True)
        ).get_response()


server.run()
