from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal

from PIL import Image

ProgressCallback = Callable[[float, str], None]
SourceKind = Literal["pdf", "image"]


class ConvertError(Exception):
    user_message = "변환에 실패했습니다."


class UnsupportedFormatError(ConvertError):
    user_message = (
        "이 파일 형식은 지원하지 않습니다.\n"
        "PDF, JPG, PNG, WEBP, BMP, TIFF만 사용할 수 있습니다."
    )


class FileOpenError(ConvertError):
    user_message = "이 파일은 열 수 없습니다.\n파일이 손상되었거나 이동되었을 수 있습니다."


class PasswordProtectedError(ConvertError):
    user_message = "암호가 걸린 PDF는 지원하지 않습니다."


class TooLargeError(ConvertError):
    user_message = "20KB 안으로 줄이지 못했습니다.\n다른 파일로 다시 시도해 주세요."


@dataclass(frozen=True)
class FileInfo:
    path: Path
    page_count: int
    kind: SourceKind


@dataclass(frozen=True)
class ConvertResult:
    jpg_bytes: bytes
    preview_image: Image.Image
    page_count: int
    used_max_side: int
    used_quality: int
    grayscale: bool

    @property
    def size(self) -> int:
        return len(self.jpg_bytes)

    @property
    def pdf_bytes(self) -> bytes:
        """하위 호환용 별칭. JPG 바이트와 동일하다."""
        return self.jpg_bytes
