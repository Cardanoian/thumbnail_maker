MAX_BYTES = 20 * 1024  # 20480. 1비트라도 초과하면 실패.
MAX_WIDTH = 400  # 출력 JPG 가로는 이 값을 넘지 않는다.
APP_NAME = "썸네일 JPG 변환기"
APP_AUTHOR = "포항원동초등학교 김지원"
FOOTER_CONTACT = f"문의: {APP_AUTHOR}"
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
MAX_WIDTHS = (400, 360, 320, 280, 240, 200, 160, 120)
QUALITY_MIN = 15
QUALITY_MAX = 85
