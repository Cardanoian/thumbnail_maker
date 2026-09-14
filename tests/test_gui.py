from pathlib import Path

import pytest

from PIL import Image

from thumbnail_maker.converter.compress import convert
from thumbnail_maker.converter.constants import FOOTER_CONTACT, MAX_BYTES, MAX_WIDTH
from thumbnail_maker.gui.fonts import FONT_FAMILY, font_dir
from thumbnail_maker.gui.window import IDLE_FILE_NAME, IDLE_PREVIEW, IDLE_STATUS, App
from tests.helpers import rgb_image, save_image


@pytest.fixture(scope="module")
def app():
    window = App()
    window.update()
    try:
        yield window
    finally:
        window.destroy()


@pytest.fixture(autouse=True)
def _reset_app(app):
    yield
    if app.winfo_exists():
        app._reset()
        app.update()


def test_gui_convert_saves_under_cap(tmp_path: Path, app: App) -> None:
    source = save_image(tmp_path / "샘플.jpg", rgb_image((640, 400), (12, 96, 180)))
    app._set_input_path(source)
    app.update()
    result = convert(source)
    app._on_success(source, result)
    app.update()
    assert app._saved_path is not None
    assert app._saved_path.exists()
    assert app._saved_path.stat().st_size <= MAX_BYTES
    assert app._saved_path.name == "샘플_20kb.jpg"
    assert app._saved_path.read_bytes().startswith(b"\xff\xd8\xff")
    with Image.open(app._saved_path) as image:
        assert image.size[0] <= MAX_WIDTH


def test_gui_reset_allows_another_file(tmp_path: Path, app: App) -> None:
    first = save_image(tmp_path / "첫번째.jpg", rgb_image((400, 300), (180, 40, 40)))
    second = save_image(tmp_path / "두번째.jpg", rgb_image((500, 320), (40, 120, 200)))
    app._set_input_path(first)
    app._on_success(first, convert(first))
    app.update()
    assert app.reset_button.cget("state") == "normal"
    assert app._saved_path is not None

    app._reset()
    app.update()
    assert app._input_path is None
    assert app._result is None
    assert app._saved_path is None
    assert app.file_name_label.cget("text") == IDLE_FILE_NAME
    assert app.status_label.cget("text") == IDLE_STATUS
    assert app.preview_label.cget("text") == IDLE_PREVIEW
    assert app.convert_button.cget("state") == "disabled"
    assert app.reset_button.cget("state") == "disabled"
    assert app.open_button.cget("state") == "disabled"
    assert app.save_as_button.cget("state") == "disabled"

    app._set_input_path(second)
    app._on_success(second, convert(second))
    app.update()
    assert app._saved_path is not None
    assert app._saved_path.name == "두번째_20kb.jpg"
    assert app._saved_path.stat().st_size <= MAX_BYTES
    with Image.open(app._saved_path) as image:
        assert image.size[0] <= MAX_WIDTH


def test_drag_and_drop_is_enabled(app: App) -> None:
    assert app._dnd_ready
    assert app.TkdndVersion


def test_pretendard_files_are_bundled() -> None:
    directory = font_dir()
    assert (directory / "Pretendard-Regular.ttf").is_file()
    assert (directory / "Pretendard-Bold.ttf").is_file()
    assert (directory / "OFL.txt").is_file()


def test_gui_uses_pretendard(app: App) -> None:
    widgets = (
        app.drop_label,
        app.file_name_label,
        app.pick_button,
        app.convert_button,
        app.reset_button,
        app.status_label,
        app.preview_label,
        app.size_label,
        app.saved_label,
        app.open_button,
        app.save_as_button,
        app.footer,
    )
    for widget in widgets:
        family = widget.cget("font").cget("family")
        assert family == FONT_FAMILY, widget


def test_footer_shows_contact(app: App) -> None:
    assert app.footer.cget("text") == FOOTER_CONTACT


def test_footer_bug_report_opens_log_prompt(monkeypatch, app: App) -> None:
    asked: dict[str, str] = {}

    def fake_askyesno(title: str, message: str) -> bool:
        asked["title"] = title
        asked["message"] = message
        return False

    monkeypatch.setattr("thumbnail_maker.gui.window.messagebox.askyesno", fake_askyesno)
    app._report_bug()
    assert asked["title"] == "문의 / 버그 신고"
    assert "포항원동초등학교 김지원" in asked["message"]
    assert "debug.log" in asked["message"]
