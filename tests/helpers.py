from io import BytesIO
from pathlib import Path

from PIL import Image
import img2pdf


def rgb_image(size=(1200, 800), color=(32, 120, 200)) -> Image.Image:
    image = Image.new("RGB", size, color)
    return image


def noisy_image(size=(1600, 1200)) -> Image.Image:
    import os

    return Image.frombytes("RGB", size, os.urandom(size[0] * size[1] * 3))


def save_image(path: Path, image: Image.Image, fmt: str = "JPEG") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {}
    if fmt == "JPEG":
        kwargs["quality"] = 90
    image.save(path, format=fmt, **kwargs)
    return path


def jpeg_bytes(image: Image.Image, quality: int = 90) -> bytes:
    buffer = BytesIO()
    rgb = image.convert("RGB")
    rgb.save(buffer, format="JPEG", quality=quality)
    return buffer.getvalue()


def write_pdf(path: Path, *images: Image.Image) -> Path:
    payloads = [jpeg_bytes(image) for image in images]
    path.write_bytes(img2pdf.convert(payloads))
    return path
