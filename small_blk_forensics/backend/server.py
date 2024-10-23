import os
from logging import Logger
from pathlib import Path
from textwrap import dedent
from typing import Optional, TypedDict

from flask_ml.flask_ml_server import MLServer
from flask_ml.flask_ml_server.models import (
    MarkdownResponse,
    ResponseBody, FileInput, DirectoryInput,
)

from small_blk_forensics.utils.common import is_dir_path
from small_blk_forensics.utils.data import MyModelResponse, Parameters

from ..ml.model import SmallBlockForensicsModel

server = MLServer(__name__)
logger = Logger(__name__)


def _execute_throws(
    parameters: Parameters,
    target_directory: Optional[str] = None,
    known_content_directory: Optional[str] = None,
    input_sql: Optional[str] = None,
    output_sql: Optional[str] = None,
) -> ResponseBody:

    if target_directory is None or not is_dir_path(target_directory):
        raise Exception(f"{target_directory} is not provided or is not a valid path")

    target_directory_path = Path(target_directory)
    del target_directory

    if not (known_content_directory or input_sql):
        raise Exception("Either known_content_directory or input_sql must be specified")

    if known_content_directory and input_sql:
        raise Exception("Both known_content_directory and input_sql cannot be specified")

    model = SmallBlockForensicsModel(parameters["block_size"], parameters["target_probability"])

    if known_content_directory:
        if not is_dir_path(known_content_directory):
            raise Exception(f"{known_content_directory} is not a valid path")

        known_content_directory_path = Path(known_content_directory)
        del known_content_directory

        if output_sql is None:
            raise Exception(f"Output_sql {output_sql} is not provided")
        output_sql_path = Path(output_sql)
        del output_sql

        logger.info(f"{known_content_directory_path}, {target_directory_path}, {output_sql_path}")

        results: MyModelResponse = model.run_with_known_content_directory(
            known_content_directory_path, target_directory_path, output_sql_path
        )
    else:
        if input_sql is None:
            raise Exception(f"{input_sql} is not a valid path")
        input_sql_path = Path(input_sql)
        del input_sql

        results = model.run_with_known_content_sqlite(input_sql_path, target_directory_path)

    return ResponseBody(
        root=MarkdownResponse(
            title="Small Block Forensics",
            value=(
                dedent(
                    f"""
                        ## Results
                        
                        - Found: {results.found}
                        - Target File: {results.target_file}
                        - Known Dataset File: {results.known_dataset_file}
                        - Block Number in Known Dataset: {results.block_num_in_known_dataset}
                        - Block Number in Target: {results.block_num_in_target}
                        """
                )
                if results.found
                else dedent(
                    f"""
                        ## Results
                        
                        - Found: {results.found}
                        """
                )
            ),
        )
    )


class InputsKnownContentDirectory(TypedDict):
    TARGET_FOLDER: DirectoryInput
    KNOWN_DATASET: DirectoryInput
    OUTPUT_SQL_PATH: FileInput


@server.route("/execute_with_known_content_directory")
def execute(inputs: InputsKnownContentDirectory, parameters: Parameters):
    try:
        return _execute_throws(
            parameters,
            inputs["TARGET_FOLDER"].path,
            inputs["KNOWN_DATASET"].path,
            None,
            inputs["OUTPUT_SQL_PATH"].path,
        )
    except Exception as e:
        logger.error("An error occurred while executing the model")
        logger.error(e)
        raise


class InputsKnownContentSql(TypedDict):
    TARGET_FOLDER: DirectoryInput
    INPUT_SQL: FileInput


@server.route("/execute_with_known_content_sql")
def execute_sql(inputs: InputsKnownContentSql, parameters: Parameters):
    try:
        return _execute_throws(parameters, inputs["TARGET_FOLDER"].path, None, inputs["INPUT_SQL"].path, None)
    except Exception as e:
        logger.error("An error occurred while executing the model")
        logger.error(e)
        raise


server.run(port=os.environ.get("FLASK_RUN_PORT") or 5000)
