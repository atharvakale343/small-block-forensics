# Command line interface for small block forensics

import argparse
from pathlib import Path

from small_blk_forensics.ml.model import SmallBlockForensicsModel
from small_blk_forensics.utils.common import dir_path_arg_parser, file_path_arg_parser


def main():
    parser = argparse.ArgumentParser(description="Analyze target directories with small block forensics")
    parser.add_argument(
        "--target_directory",
        type=dir_path_arg_parser,
        help="The path to the directory containing files/folders of the content to analyze",
        required=True,
    )
    parser.add_argument(
        "--output_directory",
        type=str,
        help="The path to the directory to save the SQLite table for known_content as well as the results",
        required=True,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--known_content_directory",
        type=dir_path_arg_parser,
        help="The path to the directory containing the files/folders of known content",
        default=None,
    )
    group.add_argument(
        "--existing_known_content_db",
        type=file_path_arg_parser,
        help="The path to the existing SQLite DB containing hashes of known content",
        default=None,
    )
    args = parser.parse_args()

    target_directory, output_directory = Path(args.target_directory), Path(args.output_directory)
    known_content_directory, existing_known_content_db = (
        args.known_content_directory,
        args.existing_known_content_db,
    )

    output_directory = Path(args.output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    model = SmallBlockForensicsModel()
    if known_content_directory:
        model.run_with_known_content_directory(
            Path(known_content_directory), target_directory, output_directory
        )
    else:
        model.run_with_known_content_sqlite(
            Path(existing_known_content_db), target_directory, output_directory
        )
    print(f"SBF for {target_directory} completed successfully!")


if __name__ == "__main__":
    main()
