from pathlib import Path

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {"image/jpeg", "image/png"}
MAX_IMAGE_DIMENSION = 4000

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

PHOTO_SIZES = {
    "1inch": {"name": "一寸", "width": 295, "height": 413, "mm": "25x35"},
    "2inch": {"name": "二寸", "width": 413, "height": 579, "mm": "35x49"},
    "small_1inch": {"name": "小一寸", "width": 260, "height": 378, "mm": "22x32"},
    "passport": {"name": "护照", "width": 390, "height": 567, "mm": "33x48"},
}

BG_COLORS = {
    "white": (255, 255, 255),
    "blue": (67, 142, 219),
    "red": (219, 37, 37),
}

FACE_CONFIDENCE_THRESHOLD = 0.5
