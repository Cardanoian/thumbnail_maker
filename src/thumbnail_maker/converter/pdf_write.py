from pathlib import Path

import img2pdf

from thumbnail_maker.converter.constants import MAX_BYTES
from thumbnail_maker.converter.types import TooLargeError


def jpeg_to_pdf(jpeg_bytes: bytes) -> bytes:
    pdf_bytes = img2pdf.convert(jpeg_bytes)
    if not isinstance(pdf_bytes, (bytes, bytearray)):
        pdf_bytes = bytes(pdf_bytes)
    return pdf_bytes


def ensure_size_cap(pdf_bytes: bytes) -> bytes:
    if len(pdf_bytes) > MAX_BYTES:
        raise TooLargeError()
    return pdf_bytes
