from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from thumbnail_maker.converter.compress import convert
from thumbnail_maker.converter.constants import MAX_BYTES
from thumbnail_maker.converter.image_write import ensure_size_cap
from thumbnail_maker.converter.loader import inspect
from thumbnail_maker.converter.paths import default_output_path
from thumbnail_maker.converter.save import save_jpg
from thumbnail_maker.converter.types import (
    FileOpenError,
    TooLargeError,
    UnsupportedFormatError,
)
from tests.helpers import noisy_image, rgb_image, save_image, write_pdf


def assert_valid_jpeg(data: bytes) -> None:
    assert data.startswith(b"\xff\xd8\xff")
    with Image.open(BytesIO(data)) as image:
        image.load()
        assert image.format == "JPEG"


def test_photo_stays_within_cap(tmp_path: Path) -> None:
    source = save_image(tmp_path / "photo.jpg", noisy_image((1800, 1200)))
    result = convert(source)
    assert result.size <= MAX_BYTES
    assert_valid_jpeg(result.jpg_bytes)


def test_small_image_is_ok_under_cap(tmp_path: Path) -> None:
    source = save_image(tmp_path / "tiny.jpg", rgb_image((80, 60), (255, 0, 0)))
    result = convert(source)
    assert result.size <= MAX_BYTES
    assert_valid_jpeg(result.jpg_bytes)


def test_alpha_png(tmp_path: Path) -> None:
    image = Image.new("RGBA", (400, 300), (10, 20, 30, 128))
    source = save_image(tmp_path / "alpha.png", image, fmt="PNG")
    result = convert(source)
    assert result.size <= MAX_BYTES
    assert result.preview_image.mode == "RGB"
    assert_valid_jpeg(result.jpg_bytes)


def test_korean_filename(tmp_path: Path) -> None:
    source = save_image(tmp_path / "여행 사진.jpg", rgb_image((640, 480)))
    result = convert(source)
    output = save_jpg(default_output_path(source), result.jpg_bytes)
    assert output.name == "여행 사진_20kb.jpg"
    assert output.stat().st_size <= MAX_BYTES
    assert_valid_jpeg(output.read_bytes())


def test_screenshot_like_image(tmp_path: Path) -> None:
    image = Image.new("RGB", (1920, 1080), (245, 245, 245))
    source = save_image(tmp_path / "screen.png", image, fmt="PNG")
    result = convert(source)
    assert result.size <= MAX_BYTES
    assert_valid_jpeg(result.jpg_bytes)


def test_single_page_pdf(tmp_path: Path) -> None:
    source = write_pdf(tmp_path / "one.pdf", rgb_image((900, 600), (0, 90, 180)))
    info = inspect(source)
    assert info.page_count == 1
    result = convert(source)
    assert result.size <= MAX_BYTES
    assert result.page_count == 1
    assert_valid_jpeg(result.jpg_bytes)


def test_multipage_pdf_uses_first_page_only(tmp_path: Path) -> None:
    source = write_pdf(
        tmp_path / "many.pdf",
        rgb_image((800, 500), (200, 30, 30)),
        rgb_image((800, 500), (30, 200, 30)),
        rgb_image((800, 500), (30, 30, 200)),
    )
    info = inspect(source)
    assert info.page_count == 3
    result = convert(source)
    assert result.page_count == 3
    assert result.size <= MAX_BYTES
    assert_valid_jpeg(result.jpg_bytes)


def test_unsupported_extension(tmp_path: Path) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")
    with pytest.raises(UnsupportedFormatError):
        inspect(path)


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileOpenError):
        inspect(tmp_path / "none.jpg")


def test_ensure_cap_rejects_oversize() -> None:
    with pytest.raises(TooLargeError):
        ensure_size_cap(b"\xff\xd8" + b"x" * MAX_BYTES)


def test_save_jpg_does_not_leave_oversize_file(tmp_path: Path) -> None:
    target = tmp_path / "out.jpg"
    with pytest.raises(TooLargeError):
        save_jpg(target, b"\xff\xd8" + b"x" * MAX_BYTES)
    assert not target.exists()


def test_saved_file_size_never_exceeds_cap(tmp_path: Path) -> None:
    source = save_image(tmp_path / "doc.jpg", noisy_image((1400, 900)))
    result = convert(source)
    output = save_jpg(tmp_path / "doc_20kb.jpg", result.jpg_bytes)
    assert output.stat().st_size <= MAX_BYTES
    assert_valid_jpeg(output.read_bytes())
