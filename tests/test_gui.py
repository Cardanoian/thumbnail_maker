from pathlib import Path

from thumbnail_maker.converter.compress import convert
from thumbnail_maker.converter.constants import MAX_BYTES
from thumbnail_maker.gui.window import IDLE_FILE_NAME, IDLE_PREVIEW, IDLE_STATUS, App
from tests.helpers import rgb_image, save_image


def test_gui_convert_saves_under_cap(tmp_path: Path) -> None:
    source = save_image(tmp_path / "샘플.jpg", rgb_image((640, 400), (12, 96, 180)))
    app = App()
    try:
        app.update()
        app._set_input_path(source)
        app.update()
        result = convert(source)
        app._on_success(source, result)
        app.update()
        assert app._saved_path is not None
        assert app._saved_path.exists()
        assert app._saved_path.stat().st_size <= MAX_BYTES
        assert app._saved_path.name == "샘플_20kb.pdf"
    finally:
        app.destroy()


def test_gui_reset_allows_another_file(tmp_path: Path) -> None:
    first = save_image(tmp_path / "첫번째.jpg", rgb_image((400, 300), (180, 40, 40)))
    second = save_image(tmp_path / "두번째.jpg", rgb_image((500, 320), (40, 120, 200)))
    app = App()
    try:
        app.update()
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
        assert app._saved_path.name == "두번째_20kb.pdf"
        assert app._saved_path.stat().st_size <= MAX_BYTES
    finally:
        app.destroy()
