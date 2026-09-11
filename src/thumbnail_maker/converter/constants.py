MAX_BYTES = 20 * 1024  # 20480. 1비트라도 초과하면 실패.
APP_NAME = "썸네일 JPG 변환기"
OUTPUT_SUFFIX = "_20kb"
SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
}
MAX_SOURCE_SIDE = 2000
PDF_RENDER_DPI = 150
MAX_SIDES = (960, 800, 640, 480, 360, 240, 160, 120)
QUALITY_MIN = 15
QUALITY_MAX = 85
