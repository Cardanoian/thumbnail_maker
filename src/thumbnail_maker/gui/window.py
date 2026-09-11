from __future__ import annotations

import logging
import subprocess
import sys
import threading
import traceback
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image

from thumbnail_maker.converter.compress import convert
from thumbnail_maker.converter.constants import APP_NAME, MAX_BYTES
from thumbnail_maker.converter.loader import inspect
from thumbnail_maker.converter.paths import default_output_path
from thumbnail_maker.converter.save import save_jpg
from thumbnail_maker.converter.types import ConvertError, ConvertResult, FileInfo
from thumbnail_maker.gui.widgets import fit_size, format_bytes, parse_dropped_paths
from thumbnail_maker.logging_setup import setup_logging

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD

    _DND_AVAILABLE = True
except Exception:
    DND_FILES = None
    TkinterDnD = None
    _DND_AVAILABLE = False

FILE_DIALOG_TYPES = [
    ("지원 파일", "*.pdf;*.jpg;*.jpeg;*.png;*.webp;*.bmp;*.tif;*.tiff"),
    ("PDF", "*.pdf"),
    ("이미지", "*.jpg;*.jpeg;*.png;*.webp;*.bmp;*.tif;*.tiff"),
    ("모든 파일", "*.*"),
]
IDLE_STATUS = "파일을 선택한 뒤 변환하기를 눌러 주세요."
IDLE_FILE_NAME = "선택된 파일이 없습니다"
IDLE_PREVIEW = "미리보기 없음"


def _dnd_base():
    if _DND_AVAILABLE:
        class CTkDnD(ctk.CTk, TkinterDnD.DnDWrapper):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.TkdndVersion = TkinterDnD._require(self)

        return CTkDnD
    return ctk.CTk


BaseApp = _dnd_base()


class App(BaseApp):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("760x640")
        self.minsize(680, 580)
        self.configure(fg_color=("#F4F6F8", "#1A1B1E"))

        self._input_path: Path | None = None
        self._file_info: FileInfo | None = None
        self._result: ConvertResult | None = None
        self._saved_path: Path | None = None
        self._busy = False
        self._preview_ctk: ctk.CTkImage | None = None

        self._build()
        self._enable_drop()

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title = ctk.CTkLabel(
            self,
            text=APP_NAME,
            font=ctk.CTkFont(size=26, weight="bold"),
        )
        title.grid(row=0, column=0, padx=28, pady=(22, 8), sticky="w")

        self.drop_frame = ctk.CTkFrame(self, corner_radius=16, fg_color=("#FFFFFF", "#2B2D31"))
        self.drop_frame.grid(row=1, column=0, padx=28, pady=8, sticky="nsew")
        self.drop_frame.grid_columnconfigure(0, weight=1)
        self.drop_frame.grid_rowconfigure(0, weight=1)

        drop_hint = (
            "파일을 여기로 끌어다 놓으세요\n또는 아래 버튼으로 파일을 선택하세요\nPDF, JPG, PNG, WEBP"
            if _DND_AVAILABLE
            else "아래 버튼으로 파일을 선택하세요\nPDF, JPG, PNG, WEBP"
        )
        self.drop_label = ctk.CTkLabel(
            self.drop_frame,
            text=drop_hint,
            font=ctk.CTkFont(size=16),
            justify="center",
        )
        self.drop_label.grid(row=0, column=0, padx=20, pady=(28, 8))

        self.file_name_label = ctk.CTkLabel(
            self.drop_frame,
            text=IDLE_FILE_NAME,
            font=ctk.CTkFont(size=14),
            text_color=("#5B6570", "#B0B6BE"),
        )
        self.file_name_label.grid(row=1, column=0, padx=20, pady=(0, 8))

        self.pick_button = ctk.CTkButton(
            self.drop_frame,
            text="파일 선택",
            width=160,
            height=40,
            font=ctk.CTkFont(size=15),
            command=self._pick_file,
        )
        self.pick_button.grid(row=2, column=0, pady=(4, 24))

        action_row = ctk.CTkFrame(self, fg_color="transparent")
        action_row.grid(row=2, column=0, padx=28, pady=(8, 8), sticky="ew")
        action_row.grid_columnconfigure(0, weight=1)

        self.convert_button = ctk.CTkButton(
            action_row,
            text="변환하기",
            height=52,
            font=ctk.CTkFont(size=20, weight="bold"),
            command=self._start_convert,
            state="disabled",
        )
        self.convert_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.reset_button = ctk.CTkButton(
            action_row,
            text="초기화",
            width=140,
            height=52,
            font=ctk.CTkFont(size=16),
            fg_color=("#E5E7EB", "#3A3D42"),
            text_color=("#1F2933", "#F4F6F8"),
            hover_color=("#D1D5DB", "#4B5563"),
            command=self._reset,
            state="disabled",
        )
        self.reset_button.grid(row=0, column=1)

        self.progress = ctk.CTkProgressBar(self, height=8)
        self.progress.grid(row=3, column=0, padx=28, pady=(4, 4), sticky="ew")
        self.progress.set(0)

        self.status_label = ctk.CTkLabel(
            self,
            text=IDLE_STATUS,
            font=ctk.CTkFont(size=14),
        )
        self.status_label.grid(row=4, column=0, padx=28, pady=(0, 8), sticky="w")

        result_frame = ctk.CTkFrame(self, corner_radius=16, fg_color=("#FFFFFF", "#2B2D31"))
        result_frame.grid(row=5, column=0, padx=28, pady=(4, 12), sticky="ew")
        result_frame.grid_columnconfigure(0, weight=1)

        self.preview_label = ctk.CTkLabel(result_frame, text=IDLE_PREVIEW, height=160)
        self.preview_label.grid(row=0, column=0, padx=16, pady=(16, 8))

        self.size_label = ctk.CTkLabel(
            result_frame,
            text="",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.size_label.grid(row=1, column=0, pady=(0, 4))

        self.saved_label = ctk.CTkLabel(
            result_frame,
            text="",
            font=ctk.CTkFont(size=13),
            text_color=("#5B6570", "#B0B6BE"),
        )
        self.saved_label.grid(row=2, column=0, pady=(0, 8))

        buttons = ctk.CTkFrame(result_frame, fg_color="transparent")
        buttons.grid(row=3, column=0, pady=(0, 16))

        self.open_button = ctk.CTkButton(
            buttons,
            text="폴더 열기",
            width=140,
            state="disabled",
            command=self._open_folder,
        )
        self.open_button.pack(side="left", padx=6)

        self.save_as_button = ctk.CTkButton(
            buttons,
            text="다른 이름으로 저장",
            width=180,
            state="disabled",
            command=self._save_as,
        )
        self.save_as_button.pack(side="left", padx=6)

    def _enable_drop(self) -> None:
        if not _DND_AVAILABLE:
            return
        for widget in (self, self.drop_frame, self.drop_label):
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self._on_drop)

    def _on_drop(self, event) -> None:
        if self._busy:
            return
        paths = parse_dropped_paths(self, event.data)
        if not paths:
            return
        if len(paths) > 1:
            messagebox.showinfo(APP_NAME, "한 번에 하나의 파일만 변환합니다.\n첫 번째 파일을 사용합니다.")
        self._set_input_path(paths[0])

    def _pick_file(self) -> None:
        if self._busy:
            return
        selected = filedialog.askopenfilename(
            title="변환할 파일 선택",
            filetypes=FILE_DIALOG_TYPES,
        )
        if selected:
            self._set_input_path(Path(selected))

    def _set_input_path(self, path: Path) -> None:
        try:
            info = inspect(path)
        except ConvertError as exc:
            messagebox.showerror(APP_NAME, exc.user_message)
            return
        except Exception:
            logging.exception("파일을 확인하지 못했습니다: %s", path)
            messagebox.showerror(APP_NAME, "이 파일은 열 수 없습니다.")
            return

        self._input_path = path
        self._file_info = info
        self._result = None
        self._saved_path = None
        self._preview_ctk = None
        self.file_name_label.configure(text=path.name)
        self.convert_button.configure(state="normal")
        self.reset_button.configure(state="normal")
        self.open_button.configure(state="disabled")
        self.save_as_button.configure(state="disabled")
        self._clear_preview()
        self.size_label.configure(text="")
        self.saved_label.configure(text="")
        self.progress.set(0)
        extra = f" (총 {info.page_count}페이지, 첫 페이지만 변환)" if info.page_count > 1 else ""
        self.status_label.configure(text=f"변환할 파일이 준비되었습니다.{extra}")

    def _start_convert(self) -> None:
        if self._busy or self._input_path is None or self._file_info is None:
            return

        if self._file_info.page_count > 1:
            ok = messagebox.askyesno(
                APP_NAME,
                f"이 PDF는 {self._file_info.page_count}페이지입니다.\n"
                "첫 페이지만 변환합니다. 계속할까요?",
            )
            if not ok:
                return

        self._set_busy(True)
        self.status_label.configure(text="화질을 맞추는 중…")
        self.progress.set(0.05)
        path = self._input_path

        worker = threading.Thread(target=self._convert_worker, args=(path,), daemon=True)
        worker.start()

    def _convert_worker(self, path: Path) -> None:
        try:
            result = convert(path, progress=self._progress_from_thread)
            self.after(0, lambda: self._on_success(path, result))
        except Exception as exc:
            logging.exception("변환 실패: %s", path)
            err = exc
            self.after(0, lambda: self._on_error(err))

    def _progress_from_thread(self, value: float, message: str) -> None:
        self.after(0, lambda: self._set_progress(value, message))

    def _set_progress(self, value: float, message: str) -> None:
        self.progress.set(max(0.0, min(1.0, value)))
        self.status_label.configure(text=message)

    def _on_success(self, path: Path, result: ConvertResult) -> None:
        self._result = result
        self._show_preview(result.preview_image)
        self.size_label.configure(
            text=f"결과  {format_bytes(result.size)} / {format_bytes(MAX_BYTES)}"
        )
        self.save_as_button.configure(state="normal")
        saved = self._auto_save(path, result)
        self._set_busy(False)
        if saved is not None:
            self._saved_path = saved
            self.saved_label.configure(text=f"저장됨: {saved.name}")
            self.open_button.configure(state="normal")
            self.status_label.configure(text="변환이 끝났습니다.")
        else:
            self.saved_label.configure(text="아직 저장하지 않았습니다. 다른 이름으로 저장을 눌러 주세요.")
            self.status_label.configure(text="변환은 끝났습니다. 저장 위치를 선택해 주세요.")
        logging.info(
            "변환 성공 size=%s quality=%s side=%s gray=%s path=%s",
            result.size,
            result.used_quality,
            result.used_max_side,
            result.grayscale,
            path,
        )

    def _auto_save(self, source: Path, result: ConvertResult) -> Path | None:
        target = default_output_path(source)
        if target.exists():
            overwrite = messagebox.askyesno(
                APP_NAME,
                f"이미 {target.name} 파일이 있습니다.\n덮어쓸까요?",
            )
            if not overwrite:
                return None
        try:
            return save_jpg(target, result.jpg_bytes)
        except ConvertError as exc:
            messagebox.showerror(APP_NAME, exc.user_message)
            return None
        except OSError:
            logging.exception("저장 실패: %s", target)
            messagebox.showerror(
                APP_NAME,
                "파일을 저장할 수 없습니다.\n다른 이름으로 저장을 시도해 주세요.",
            )
            return None

    def _on_error(self, exc: BaseException) -> None:
        self._set_busy(False)
        self.progress.set(0)
        message = exc.user_message if isinstance(exc, ConvertError) else (
            "변환에 실패했습니다.\n파일이 손상되었는지 확인해 주세요."
        )
        self.status_label.configure(text="변환에 실패했습니다.")
        logging.error("변환 오류: %s\n%s", exc, traceback.format_exc())
        messagebox.showerror(APP_NAME, message)

    def _reset(self) -> None:
        if self._busy:
            return
        self._input_path = None
        self._file_info = None
        self._result = None
        self._saved_path = None
        self._preview_ctk = None
        self.file_name_label.configure(text=IDLE_FILE_NAME)
        self.convert_button.configure(state="disabled")
        self.reset_button.configure(state="disabled")
        self.open_button.configure(state="disabled")
        self.save_as_button.configure(state="disabled")
        self._clear_preview()
        self.size_label.configure(text="")
        self.saved_label.configure(text="")
        self.progress.set(0)
        self.status_label.configure(text=IDLE_STATUS)

    def _save_as(self) -> None:
        if self._result is None:
            return
        initial = default_output_path(self._input_path) if self._input_path else Path("thumbnail_20kb.jpg")
        selected = filedialog.asksaveasfilename(
            title="JPG 저장",
            defaultextension=".jpg",
            initialfile=initial.name,
            initialdir=str(initial.parent),
            filetypes=[("JPEG", "*.jpg;*.jpeg")],
        )
        if not selected:
            return
        try:
            saved = save_jpg(Path(selected), self._result.jpg_bytes)
        except ConvertError as exc:
            messagebox.showerror(APP_NAME, exc.user_message)
            return
        except OSError:
            logging.exception("다른 이름으로 저장 실패")
            messagebox.showerror(APP_NAME, "파일을 저장할 수 없습니다.")
            return
        self._saved_path = saved
        self.saved_label.configure(text=f"저장됨: {saved.name}")
        self.open_button.configure(state="normal")
        self.status_label.configure(text="저장했습니다.")

    def _open_folder(self) -> None:
        if self._saved_path is None or not self._saved_path.exists():
            return
        path = str(self._saved_path.resolve())
        if sys.platform == "win32":
            subprocess.run(["explorer", "/select,", path], check=False)
        else:
            subprocess.run(["xdg-open", str(self._saved_path.parent)], check=False)

    def _clear_preview(self) -> None:
        inner = getattr(self.preview_label, "_label", None)
        if inner is not None:
            inner.configure(image="")
        self.preview_label.configure(image="", text=IDLE_PREVIEW)
        self._preview_ctk = None

    def _show_preview(self, image: Image.Image) -> None:
        size = fit_size(image, (420, 180))
        preview = image.copy()
        preview.thumbnail(size, Image.Resampling.LANCZOS)
        self._preview_ctk = ctk.CTkImage(
            light_image=preview,
            dark_image=preview,
            size=preview.size,
        )
        self.preview_label.configure(image=self._preview_ctk, text="")

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = "disabled" if busy else "normal"
        self.pick_button.configure(state=state)
        self.convert_button.configure(state="disabled" if busy or self._input_path is None else "normal")
        self.reset_button.configure(
            state="disabled" if busy or not self._can_reset() else "normal"
        )
        if busy:
            self.open_button.configure(state="disabled")
            self.save_as_button.configure(state="disabled")

    def _can_reset(self) -> bool:
        return self._input_path is not None or self._result is not None


def run_app() -> None:
    setup_logging()
    logging.info("앱 시작")
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
