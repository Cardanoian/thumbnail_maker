# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_dynamic_libs

spec_dir = Path(SPECPATH)
root = spec_dir.parent
src = root / "src"
icon = root / "assets" / "icon.ico"

datas = []
binaries = []
hiddenimports = [
    "PIL._tkinter_finder",
    "tkinterdnd2",
    "customtkinter",
    "pypdfium2",
]

for pkg in ("customtkinter", "tkinterdnd2", "pypdfium2"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

datas += collect_data_files("customtkinter")
datas += collect_data_files("tkinterdnd2")
binaries += collect_dynamic_libs("pypdfium2")

if icon.exists():
    datas.append((str(icon), "assets"))

fonts = root / "assets" / "fonts"
if fonts.exists():
    for font_file in fonts.iterdir():
        if font_file.is_file():
            datas.append((str(font_file), "assets/fonts"))

a = Analysis(
    [str(src / "thumbnail_maker" / "app.py")],
    pathex=[str(src)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ThumbnailMaker",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=str(icon) if icon.exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="ThumbnailMaker",
)
