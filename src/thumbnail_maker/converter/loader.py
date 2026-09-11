from pathlib import Path

from PIL import Image, ImageOps

from thumbnail_maker.converter.constants import (
    MAX_SOURCE_SIDE,
    PDF_RENDER_DPI,
    SUPPORTED_EXTENSIONS,
)
from thumbnail_maker.converter.types import (
    FileInfo,
    FileOpenError,
    PasswordProtectedError,
    UnsupportedFormatError,
)


def inspect(path: Path) -> FileInfo:
    path = Path(path)
    if not path.is_file():
        raise FileOpenError()

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFormatError()

    if ext == ".pdf":
        return FileInfo(path=path, page_count=_pdf_page_count(path), kind="pdf")

    try:
        with Image.open(path) as image:
            image.verify()
    except Exception as exc:
        raise FileOpenError() from exc

    return FileInfo(path=path, page_count=1, kind="image")


def load_rgb_image(path: Path) -> tuple[Image.Image, int]:
    info = inspect(path)
    if info.kind == "pdf":
        image = _render_pdf_first_page(path)
    else:
        image = _load_raster(path)
    return _prepare_rgb(image), info.page_count


def _pdf_page_count(path: Path) -> int:
    import pypdfium2 as pdfium

    try:
        document = pdfium.PdfDocument(str(path))
    except Exception as exc:
        if _is_password_error(exc):
            raise PasswordProtectedError() from exc
        raise FileOpenError() from exc

    try:
        return len(document)
    finally:
        document.close()


def _render_pdf_first_page(path: Path) -> Image.Image:
    import pypdfium2 as pdfium

    try:
        document = pdfium.PdfDocument(str(path))
    except Exception as extra:
        if _is_password_error(extra):
            raise PasswordProtectedError() from extra
        raise FileOpenError() from extra

    try:
        if len(document) < 1:
            raise FileOpenError()
        page = document[0]
        bitmap = page.render(scale=PDF_RENDER_DPI / 72)
        return bitmap.to_pil()
    except (FileOpenError, PasswordProtectedError):
        raise
    except Exception as extra:
        raise FileOpenError() from extra
    finally:
        document.close()


def _load_raster(path: Path) -> Image.Image:
    try:
        with Image.open(path) as image:
            image = ImageOps.exif_transpose(image)
            return image.copy()
    except Exception as extra:
        raise FileOpenError() from extra


def _prepare_rgb(image: Image.Image) -> Image.Image:
    if image.mode in ("RGBA", "LA") or (
        image.mode == "P" and "transparency" in image.info
    ):
        rgba = image.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        image = Image.alpha_composite(background, rgba).convert("RGB")
    elif image.mode == "L":
        image = image.convert("RGB")
    elif image.mode != "RGB":
        image = image.convert("RGB")

    return _limit_source_side(image)


def _limit_source_side(image: Image.Image) -> Image.Image:
    width, height = image.size
    longest = max(width, height)
    if longest <= MAX_SOURCE_SIDE:
        return image
    scale = MAX_SOURCE_SIDE / longest
    new_size = (max(1, round(width * scale)), max(1, round(height * scale)))
    return image.resize(new_size, Image.Resampling.LANCZOS)


def _is_password_error(exc: BaseException) -> bool:
    text = str(exc).lower()
    return "password" in text or "passwd" in text or "encrypted" in text
