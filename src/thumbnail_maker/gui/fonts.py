from __future__ import annotations

import logging
import sys
from pathlib import Path
from tkinter import font as tkfont
from typing import Literal

import customtkinter as ctk
from customtkinter.windows.widgets.font import FontManager
from customtkinter.windows.widgets.theme import ThemeManager

FONT_FAMILY = "Pretendard"
_FONT_FILES = ("Pretendard-Regular.ttf", "Pretendard-Bold.ttf")
_files_loaded = False


def font_dir() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    else:
        base = Path(__file__).resolve().parents[3]
    return base / "assets" / "fonts"


def load_pretendard() -> None:
    global _files_loaded
    if _files_loaded:
        return
    directory = font_dir()
    loaded_any = False
    for name in _FONT_FILES:
        path = directory / name
        if not path.is_file():
            logging.warning("Pretendard 파일을 찾지 못했습니다: %s", path)
            continue
        if FontManager.load_font(str(path)):
            loaded_any = True
        else:
            logging.warning("Pretendard를 등록하지 못했습니다: %s", path)
    _files_loaded = True
    if loaded_any:
        logging.info("Pretendard 글꼴을 등록했습니다.")


def apply_pretendard_theme() -> None:
    theme_font = ThemeManager.theme.get("CTkFont")
    if isinstance(theme_font, dict) and "family" in theme_font:
        theme_font["family"] = FONT_FAMILY


def apply_tk_named_fonts() -> None:
    for name in (
        "TkDefaultFont",
        "TkTextFont",
        "TkMenuFont",
        "TkHeadingFont",
        "TkCaptionFont",
        "TkSmallCaptionFont",
        "TkIconFont",
        "TkTooltipFont",
    ):
        try:
            tkfont.nametofont(name).configure(family=FONT_FAMILY)
        except tkfont.TclError:
            continue


def apply_pretendard() -> None:
    load_pretendard()
    apply_pretendard_theme()


def ui_font(size: int, weight: Literal["normal", "bold"] = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)
