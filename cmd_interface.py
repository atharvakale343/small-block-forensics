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
    parser.add_argument(
        "--target_probability",
        type=float,
        help="The target probability to achieve. Higher means more of the target drive will be scanned. Defaults to 0.95",
        default=0.95,
        required=False,
    )
    parser.add_argument(
        "--block_size",
        type=int,
        help="The block size in bytes to be used. Defaults to 4096.",
        default=4096,
        required=False,
    )
    args = parser.parse_args()

    target_directory, output_directory = Path(args.target_directory), Path(args.output_directory)
    known_content_directory, existing_known_content_db = (
        args.known_content_directory,
        args.existing_known_content_db,
    )

    output_directory = Path(args.output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    model = SmallBlockForensicsModel(args.block_size, args.target_probability)
    print()
    if known_content_directory:
        result = model.run_with_known_content_directory(
            Path(known_content_directory), target_directory, output_directory
        )
    else:
        result = model.run_with_known_content_sqlite(Path(existing_known_content_db), target_directory)

    print("Results:")
    print(f"\tMatch: {"Yes" if result.found else "No"}")
    print(f"\tTarget Probability: {args.target_probability}")
    print(f"\tBlock Size: {args.block_size}")
    if result.found:
        print(f"\tMatched Target File: {result.target_file}")
        print(f"\tMatch Known Dataset File: {result.known_dataset_file}")
        print(f"\tBlock Num in Known Dataset File: {result.block_num_in_known_dataset}")
        print(f"\tBlock Num in Target File: {result.block_num_in_target}")


if __name__ == "__main__":
    main()
