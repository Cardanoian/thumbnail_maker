from thumbnail_maker.converter.constants import MAX_BYTES
from thumbnail_maker.converter.types import TooLargeError


def ensure_size_cap(data: bytes) -> bytes:
    if len(data) > MAX_BYTES:
        raise TooLargeError()
    return data
