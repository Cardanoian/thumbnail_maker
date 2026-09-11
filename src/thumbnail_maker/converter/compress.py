from io import BytesIO

from PIL import Image

from thumbnail_maker.converter.constants import (
    MAX_BYTES,
    MAX_SIDES,
    QUALITY_MAX,
    QUALITY_MIN,
)
from thumbnail_maker.converter.loader import load_rgb_image
from thumbnail_maker.converter.image_write import ensure_size_cap
from thumbnail_maker.converter.types import ConvertResult, ProgressCallback, TooLargeError


def convert(path, progress: ProgressCallback | None = None) -> ConvertResult:
    image, page_count = load_rgb_image(path)
    _report(progress, 0.05, "이미지를 준비하는 중…")

    modes = (("RGB", False, image), ("L", True, image.convert("L")))
    attempts = 0
    total = len(modes) * len(MAX_SIDES)

    for _mode_name, grayscale, work_image in modes:
        for max_side in MAX_SIDES:
            attempts += 1
            _report(
                progress,
                0.05 + 0.9 * (attempts / total),
                "화질을 맞추는 중…",
            )
            resized = _fit(work_image, max_side)
            found = _best_quality_jpeg(resized)
            if found is None:
                continue
            jpg_bytes, quality = found
            ensure_size_cap(jpg_bytes)
            preview = resized.convert("RGB") if grayscale else resized
            _report(progress, 1.0, "변환을 마쳤습니다.")
            return ConvertResult(
                jpg_bytes=jpg_bytes,
                preview_image=preview.copy(),
                page_count=page_count,
                used_max_side=max(resized.size),
                used_quality=quality,
                grayscale=grayscale,
            )

    raise TooLargeError()


def _fit(image: Image.Image, max_side: int) -> Image.Image:
    width, height = image.size
    longest = max(width, height)
    if longest <= max_side:
        return image
    scale = max_side / longest
    new_size = (max(1, round(width * scale)), max(1, round(height * scale)))
    return image.resize(new_size, Image.Resampling.LANCZOS)


def _best_quality_jpeg(image: Image.Image) -> tuple[bytes, int] | None:
    low = QUALITY_MIN
    high = QUALITY_MAX
    best: tuple[bytes, int] | None = None

    while low <= high:
        quality = (low + high) // 2
        data = _jpeg_bytes(image, quality)
        if len(data) <= MAX_BYTES:
            best = (data, quality)
            low = quality + 1
        else:
            high = quality - 1

    return best


def _best_quality_pdf(image: Image.Image) -> tuple[bytes, int] | None:
    """하위 호환용 별칭. JPG 기준 탐색과 동일하다."""
    return _best_quality_jpeg(image)


def _jpeg_bytes(image: Image.Image, quality: int) -> bytes:
    buffer = BytesIO()
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")
    kwargs = {
        "format": "JPEG",
        "quality": quality,
        "optimize": True,
        "progressive": False,
    }
    if image.mode == "RGB":
        kwargs["subsampling"] = 2
    image.save(buffer, **kwargs)
    return buffer.getvalue()


def _report(progress: ProgressCallback | None, value: float, message: str) -> None:
    if progress is not None:
        progress(value, message)
