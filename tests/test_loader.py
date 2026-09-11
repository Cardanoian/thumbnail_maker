from pathlib import Path

from thumbnail_maker.converter.loader import inspect
from thumbnail_maker.converter.paths import default_output_path
from tests.helpers import rgb_image, save_image, write_pdf


def test_inspect_image(tmp_path: Path) -> None:
    source = save_image(tmp_path / "a.webp", rgb_image((50, 40)), fmt="WEBP")
    info = inspect(source)
    assert info.kind == "image"
    assert info.page_count == 1


def test_inspect_pdf(tmp_path: Path) -> None:
    source = write_pdf(tmp_path / "a.pdf", rgb_image((100, 80)), rgb_image((100, 80)))
    info = inspect(source)
    assert info.kind == "pdf"
    assert info.page_count == 2


def test_default_output_path(tmp_path: Path) -> None:
    assert default_output_path(tmp_path / "photo.jpg").name == "photo_20kb.jpg"
    assert default_output_path(Path("scan.PDF")).name == "scan_20kb.jpg"
    assert default_output_path(tmp_path / "scan.PDF").suffix == ".jpg"
