from pathlib import Path

from thumbnail_maker.converter.compress import convert
from thumbnail_maker.converter.constants import MAX_BYTES
from thumbnail_maker.converter.pdf_write import ensure_size_cap
from thumbnail_maker.converter.types import TooLargeError


def save_pdf(output_path: Path, pdf_bytes: bytes) -> Path:
    ensure_size_cap(pdf_bytes)
    output_path = Path(output_path)
    output_path.write_bytes(pdf_bytes)
    size = output_path.stat().st_size
    if size > MAX_BYTES:
        output_path.unlink(missing_ok=True)
        raise TooLargeError()
    return output_path
