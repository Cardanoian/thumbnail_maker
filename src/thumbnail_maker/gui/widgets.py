from pathlib import Path
from PIL import Image


def format_bytes(size: int) -> str:
    return f"{size / 1024:.1f} KB"


def fit_size(image: Image.Image, box: tuple[int, int]) -> tuple[int, int]:
    width, height = image.size
    if width <= 0 or height <= 0:
        return (1, 1)
    scale = min(box[0] / width, box[1] / height)
    return (max(1, int(width * scale)), max(1, int(height * scale)))


def parse_dropped_paths(root, data: str) -> list[Path]:
    parts = root.tk.splitlist(data)
    return [Path(part) for part in parts if part]
