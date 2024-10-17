from logging import Logger
import os
from pathlib import Path

from flask import Response
from flask_ml.flask_ml_server import MLServer
from flask_ml.flask_ml_server.constants import DataTypes
from flask_ml.flask_ml_server.models import (
    CustomInput,
    ErrorResponseModel,
    ResponseModel,
    TextResult,
)
from pydantic import ValidationError

from small_blk_forensics.utils.common import is_dir_path
from small_blk_forensics.utils.data import InputTypeKey, MyModelRequest, _Parameters

from ..ml.model import SmallBlockForensicsModel

server = MLServer(__name__)
logger = Logger(__name__)


def _execute_throws(inputs: list[CustomInput], parameters: _Parameters) -> Response:
    try:
        model_request = MyModelRequest(data_type=DataTypes.CUSTOM, inputs=inputs, parameters=parameters)  # type: ignore
    except ValidationError as e:
        return ErrorResponseModel(errors=[str(e)]).get_response()

    target_directory, known_content_directory, input_sql, output_sql = (
        None,
        None,
        None,
        None,
    )
    for inp in model_request.inputs:
        if inp.input["input_type"] == InputTypeKey.TARGET_FOLDER.value:
            target_directory = inp.input["file_path"]
        if inp.input["input_type"] == InputTypeKey.KNOWN_DATASET.value:
            known_content_directory = inp.input["file_path"]
        if inp.input["input_type"] == InputTypeKey.INPUT_SQL.value:
            input_sql = inp.input["file_path"]
        if inp.input["input_type"] == InputTypeKey.OUTPUT_SQL_PATH.value:
            output_sql = inp.input["file_path"]

    if target_directory is None or not is_dir_path(target_directory):
        return ErrorResponseModel(
            errors=[
                f"{InputTypeKey.TARGET_FOLDER.value} {target_directory} is not provided or is not a valid path"
            ],
        ).get_response()
    target_directory_path = Path(target_directory)
    del target_directory

    if not (known_content_directory or input_sql):
        return ErrorResponseModel(
            errors=[
                f"Either {InputTypeKey.KNOWN_DATASET.value} or {InputTypeKey.INPUT_SQL.value} must be specified"
            ],
        ).get_response()

    if known_content_directory and input_sql:
        return ErrorResponseModel(
            errors=[
                f"Both {InputTypeKey.KNOWN_DATASET.value} and {InputTypeKey.INPUT_SQL.value} cannot be specified"
            ],
        ).get_response()

    model = SmallBlockForensicsModel(
        model_request.parameters.block_size, model_request.parameters.target_probability
    )

    if known_content_directory:
        if not is_dir_path(known_content_directory):
            return ErrorResponseModel(
                errors=[f"{known_content_directory} is not a valid path"]
            ).get_response()
        known_content_directory_path = Path(known_content_directory)
        del known_content_directory

        if output_sql is None:
            return ErrorResponseModel(
                errors=[f"{InputTypeKey.OUTPUT_SQL_PATH.value} {output_sql} is not provided"],
            ).get_response()
        output_sql_path = Path(output_sql)
        del output_sql

        logger.info(f"{known_content_directory_path}, {target_directory_path}, {output_sql_path}")

        return ResponseModel(
            results=[
                TextResult(
                    result=model.run_with_known_content_directory(
                        known_content_directory_path, target_directory_path, output_sql_path
                    ).model_dump(exclude_none=True),
                    text="RESULTS",
                ),
                TextResult(result=str(output_sql_path), text="Successfully stored hashes"),
            ]
        ).get_response()
    else:
        if input_sql is None:
            return ErrorResponseModel(errors=[f"{input_sql} is not a valid path"]).get_response()
        input_sql_path = Path(input_sql)
        del input_sql

        return ResponseModel(
            results=[
                TextResult(
                    result=model.run_with_known_content_sqlite(
                        input_sql_path, target_directory_path
                    ).model_dump(exclude_none=True),
                    text="RESULTS",
                )
            ]
        ).get_response()


@server.route("/execute", input_type=DataTypes.CUSTOM)
def execute(inputs: list[CustomInput], parameters: dict):
    try:
        return _execute_throws(
            inputs,
            _Parameters(
                block_size=parameters["block_size"], target_probability=parameters["target_probability"]
            ),
        )
    except Exception as e:
        logger.error('An error occurred while executing the model')
        logger.error(e)
        return ErrorResponseModel(errors=[f"Server Error: {str(e)}"]).get_response(500)


server.run(port=os.environ.get('FLASK_RUN_PORT') or 5000)
