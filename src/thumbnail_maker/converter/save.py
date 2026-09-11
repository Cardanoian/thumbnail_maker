from pathlib import Path

from thumbnail_maker.converter.compress import convert
from thumbnail_maker.converter.constants import MAX_BYTES
from thumbnail_maker.converter.image_write import ensure_size_cap
from thumbnail_maker.converter.types import TooLargeError


def save_jpg(output_path: Path, jpg_bytes: bytes) -> Path:
    ensure_size_cap(jpg_bytes)
    output_path = Path(output_path)
    output_path.write_bytes(jpg_bytes)
    size = output_path.stat().st_size
    if size > MAX_BYTES:
        output_path.unlink(missing_ok=True)
        raise TooLargeError()
    return output_path


def save_pdf(output_path: Path, data: bytes) -> Path:
    """하위 호환용 별칭."""
    return save_jpg(output_path, data)
