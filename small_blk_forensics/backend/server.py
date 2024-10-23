import os
from logging import Logger
from pathlib import Path
from textwrap import dedent
from typing import Optional, TypedDict

from flask_ml.flask_ml_server import MLServer
from flask_ml.flask_ml_server.models import (
    DirectoryInput,
    FileInput,
    FloatRangeDescriptor,
    InputSchema,
    InputType,
    IntRangeDescriptor,
    MarkdownResponse,
    ParameterSchema,
    RangedFloatParameterDescriptor,
    RangedIntParameterDescriptor,
    ResponseBody,
    TaskSchema,
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


def task_schema_func_known_directory():
    return TaskSchema(
        inputs=[
            InputSchema(
                key="target_folder",
                label="Target Directory",
                subtitle="The directory containing files/folders of the content to analyze",
                input_type=InputType.DIRECTORY,
            ),
            InputSchema(
                key="known_dataset",
                label="Known Content Directory",
                subtitle="The directory containing the files/folders of known content",
                input_type=InputType.DIRECTORY,
            ),
            InputSchema(
                key="output_sql_path",
                label="Output SQL Path",
                subtitle="The path to save the SQLite table for known_content",
                input_type=InputType.FILE,
            ),
        ],
        parameters=[
            ParameterSchema(
                key="block_size",
                label="Block Size",
                subtitle="The block size in bytes to be used. Defaults to 4096.",
                value=RangedIntParameterDescriptor(range=IntRangeDescriptor(min=1, max=1024), default=4096),
            ),
            ParameterSchema(
                key="target_probability",
                label="Target Probability",
                subtitle="The target probability to achieve. Higher means more of the target drive will be scanned. Defaults to 0.95",
                value=RangedFloatParameterDescriptor(
                    range=FloatRangeDescriptor(
                        min=0,
                        max=1,
                    ),
                    default=0.95,
                ),
            ),
        ],
    )


class InputsKnownContentDirectory(TypedDict):
    target_folder: DirectoryInput
    known_dataset: DirectoryInput
    output_sql_path: FileInput


@server.route(
    "/gen_hash_random",
    task_schema_func=task_schema_func_known_directory,
    short_title="Hash random blocks of a target directory",
    order=0,
)
def execute(inputs: InputsKnownContentDirectory, parameters: Parameters):
    try:
        return _execute_throws(
            parameters,
            inputs["target_folder"].path,
            inputs["known_dataset"].path,
            None,
            inputs["output_sql_path"].path,
        )
    except Exception as e:
        logger.error("An error occurred while executing the model")
        logger.error(e)
        raise


def task_schema_func_known_sql():
    return TaskSchema(
        inputs=[
            InputSchema(
                key="target_folder",
                label="Target Directory",
                subtitle="The directory containing files/folders of the content to analyze",
                input_type=InputType.DIRECTORY,
            ),
            InputSchema(
                key="input_sql",
                label="Input SQL",
                subtitle="The path to the existing SQLite DB containing hashes of known content",
                input_type=InputType.FILE,
            ),
        ],
        parameters=[
            ParameterSchema(
                key="block_size",
                label="Block Size",
                value=RangedIntParameterDescriptor(range=IntRangeDescriptor(min=1, max=1024), default=4096),
            ),
            ParameterSchema(
                key="target_probability",
                label="Target Probability",
                value=RangedFloatParameterDescriptor(
                    range=FloatRangeDescriptor(
                        min=0,
                        max=1,
                    ),
                    default=0.95,
                ),
            ),
        ],
    )


class InputsKnownContentSql(TypedDict):
    target_folder: DirectoryInput
    input_sql: FileInput


@server.route(
    "/hash_random",
    task_schema_func=task_schema_func_known_sql,
    order=1,
    short_title="Hash random blocks of a target directory with seed DB",
)
def execute_sql(inputs: InputsKnownContentSql, parameters: Parameters):
    try:
        return _execute_throws(parameters, inputs["target_folder"].path, None, inputs["input_sql"].path, None)
    except Exception as e:
        logger.error("An error occurred while executing the model")
        logger.error(e)
        raise


def task_schema_func_gen_hash():
    return TaskSchema(
        inputs=[
            InputSchema(
                key="known_content_directory",
                label="Known Content Directory",
                subtitle="The directory containing the files/folders of known content",
                input_type=InputType.DIRECTORY,
            ),
            InputSchema(
                key="output_sql_path",
                label="Output SQL Path",
                subtitle="The path to save the SQLite table for known_content",
                input_type=InputType.FILE,
            ),
        ],
        parameters=[
            ParameterSchema(
                key="block_size",
                label="Block Size",
                subtitle="The block size in bytes to be used. Defaults to 4096.",
                value=RangedIntParameterDescriptor(range=IntRangeDescriptor(min=1, max=1024), default=4096),
            ),
        ],
    )


class InputsGenerateSqlDb(TypedDict):
    known_content_directory: DirectoryInput
    output_sql_path: FileInput


class ParametersGenerateSqlDb(TypedDict):
    block_size: int


@server.route(
    "/gen_hash",
    task_schema_func=task_schema_func_gen_hash,
    short_title="Generate SQLite DB of Hashes",
    order=2,
)
def execute_gen_hash(inputs: InputsGenerateSqlDb, parameters: ParametersGenerateSqlDb):
    model = SmallBlockForensicsModel(parameters["block_size"])
    model.hash_directory(Path(inputs["known_content_directory"].path), Path(inputs["output_sql_path"].path))
    return ResponseBody(
        root=MarkdownResponse(
            title="Small Block Forensics",
            value=dedent(
                f"""
        ## Results
        
        - Successfully generated SQLite DB at {inputs["output_sql_path"].path}
    """
            ),
        )
    )


if __name__ == "__main__":
    server.run(port=os.environ.get("FLASK_RUN_PORT") or 5000)
