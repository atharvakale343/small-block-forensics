import os


def is_dir_path(path: str) -> bool:
    return os.path.isdir(path)  # type: ignore


def dir_path_arg_parser(path: str) -> str:
    if is_dir_path(path):
        return path
    else:
        raise NotADirectoryError(f"{path} is not a directory")


def file_path_arg_parser(path: str) -> str:
    if path and os.path.isfile(path):
        return path
    else:
        raise FileNotFoundError(f"{path} not found")
