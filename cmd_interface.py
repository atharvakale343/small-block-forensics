# Command line interface for small block forensics

import argparse
from pathlib import Path

from small_blk_forensics.ml.model import SmallBlockForensicsModel
from small_blk_forensics.utils.common import dir_path_arg_parser, file_path_arg_parser
from small_blk_forensics.utils.data import MyModelResponse


def _ensure_output_file_path(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


def _print_results(result: MyModelResponse, args: argparse.Namespace):
    print("Results:")
    print(f"\tMatch: {"Yes" if result.found else "No"}")
    print(f"\tTarget Probability: {args.target_probability}")
    print(f"\tBlock Size: {args.block_size}")
    if result.found:
        print(f"\tMatched Target File: {result.target_file}")
        print(f"\tMatch Known Dataset File: {result.known_dataset_file}")
        print(f"\tBlock Num in Known Dataset File: {result.block_num_in_known_dataset}")
        print(f"\tBlock Num in Target File: {result.block_num_in_target}")


def combined_parser_func(args: argparse.Namespace):
    output_sql_file = Path(args.output_sql)
    _ensure_output_file_path(output_sql_file)

    model = SmallBlockForensicsModel(args.block_size, args.target_probability)
    result = model.run_with_known_content_directory(
        Path(args.known_content_directory), Path(args.target_directory), output_sql_file
    )

    _print_results(result, args)


def generate_hashes_parser_func(args: argparse.Namespace):
    output_sql = Path(args.output_sql)
    _ensure_output_file_path(output_sql)

    model = SmallBlockForensicsModel(args.block_size)
    model.hash_directory(Path(args.known_content_directory), output_sql)
    print()


def hash_random_blocks_parser_func(args: argparse.Namespace):
    model = SmallBlockForensicsModel(args.block_size, args.target_probability)
    result = model.run_with_known_content_sqlite(Path(args.input_sql), Path(args.target_directory))

    _print_results(result, args)


def main():
    parser = argparse.ArgumentParser(description="Analyze target directories with small block forensics")
    subparsers = parser.add_subparsers(help="Subcommands", required=True)

    # Combined Parser
    combined_parser = subparsers.add_parser(
        "gen_hash_and_hash_random",
        help="Hash random blocks of a target directory and check against hashes of blocks contained within a source directory",
    )
    combined_parser.set_defaults(func=combined_parser_func)
    combined_parser.add_argument(
        "--target_directory",
        type=dir_path_arg_parser,
        help="The path to the directory containing files/folders of the content to analyze",
        required=True,
    )
    combined_parser.add_argument(
        "--output_sql",
        type=str,
        help="The path to save the SQLite table for known_content",
        required=True,
    )
    combined_parser.add_argument(
        "--known_content_directory",
        type=dir_path_arg_parser,
        help="The path to the directory containing the files/folders of known content",
        default=None,
    )
    combined_parser.add_argument(
        "--target_probability",
        type=float,
        help="The target probability to achieve. Higher means more of the target drive will be scanned. Defaults to 0.95",
        default=0.95,
        required=False,
    )
    combined_parser.add_argument(
        "--block_size",
        type=int,
        help="The block size in bytes to be used. Defaults to 4096.",
        default=4096,
        required=False,
    )

    # Generate hashes parser
    generate_hashes_parser = subparsers.add_parser(
        "generate_hashes",
        help="Generate a SQLite DB contains hashes of all the blocks within a source directory",
    )
    generate_hashes_parser.set_defaults(func=generate_hashes_parser_func)
    generate_hashes_parser.add_argument(
        "--output_sql",
        type=str,
        help="The path to save the SQLite table for known_content",
        required=True,
    )
    generate_hashes_parser.add_argument(
        "--known_content_directory",
        type=dir_path_arg_parser,
        help="The path to the directory containing the files/folders of known content",
        default=None,
    )
    generate_hashes_parser.add_argument(
        "--block_size",
        type=int,
        help="The block size in bytes to be used. Defaults to 4096.",
        default=4096,
        required=False,
    )

    # Hash Random blocks parser
    hash_random_blocks_parser = subparsers.add_parser(
        "hash_random_blocks",
        help="Hash random blocks of a target directory and check against hashes contained within an SQLite DB",
    )
    hash_random_blocks_parser.set_defaults(func=hash_random_blocks_parser_func)
    hash_random_blocks_parser.add_argument(
        "--input_sql",
        type=file_path_arg_parser,
        help="The path to the existing SQLite DB containing hashes of known content",
        default=None,
    )
    hash_random_blocks_parser.add_argument(
        "--target_directory",
        type=dir_path_arg_parser,
        help="The path to the directory containing files/folders of the content to analyze",
        required=True,
    )
    hash_random_blocks_parser.add_argument(
        "--target_probability",
        type=float,
        help="The target probability to achieve. Higher means more of the target drive will be scanned. Defaults to 0.95",
        default=0.95,
        required=False,
    )
    hash_random_blocks_parser.add_argument(
        "--block_size",
        type=int,
        help="The block size in bytes to be used. Defaults to 4096.",
        default=4096,
        required=False,
    )
    args = parser.parse_args()
    if args.func:
        print()
        args.func(args)


if __name__ == "__main__":
    main()
