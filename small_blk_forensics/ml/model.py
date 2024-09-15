from pathlib import Path

from small_blk_forensics.utils.data import ModelResponse


class SmallBlockForensicsModel:
    def __init__(self, model_path: str = "base"): ...

    def run_with_known_content_directory(
        self, known_content_directory: Path, target_directory: Path, out_dir: Path
    ) -> ModelResponse:
        return ModelResponse(found=False)

    def run_with_known_content_sqlite(
        self, known_content_sqlite: Path, target_directory: Path, out_dir: Path
    ) -> ModelResponse:
        return ModelResponse(found=False)
