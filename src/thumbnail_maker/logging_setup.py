import logging
import os
import sys
from pathlib import Path


def log_file_path() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", str(Path.home()))) / "ThumbnailMaker"
    else:
        base = Path.home() / ".thumbnail_maker"
    return base / "debug.log"


def setup_logging() -> Path:
    log_path = log_file_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    handlers: list[logging.Handler] = [
        logging.FileHandler(log_path, encoding="utf-8"),
    ]
    if not getattr(sys, "frozen", False):
        handlers.append(logging.StreamHandler(sys.stderr))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=handlers,
        force=True,
    )
    return log_path
