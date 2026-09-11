from pathlib import Path

from thumbnail_maker.converter.constants import OUTPUT_SUFFIX


def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(f"{input_path.stem}{OUTPUT_SUFFIX}.jpg")
