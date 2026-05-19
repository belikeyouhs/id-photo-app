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
    "small_2inch": {"name": "小二寸", "width": 413, "height": 531, "mm": "35x45"},
    "large_1inch": {"name": "大一寸", "width": 390, "height": 567, "mm": "33x48"},
    "large_2inch": {"name": "大二寸", "width": 413, "height": 626, "mm": "35x53"},
    "passport": {"name": "护照", "width": 390, "height": 567, "mm": "33x48"},
    "visa_us": {"name": "美国签证", "width": 600, "height": 600, "mm": "51x51"},
    "visa_japan": {"name": "日本签证", "width": 531, "height": 531, "mm": "45x45"},
    "id_card": {"name": "身份证", "width": 308, "height": 378, "mm": "26x32"},
    "driver_license": {"name": "驾驶证", "width": 260, "height": 378, "mm": "22x32"},
}

BG_COLORS = {
    "white": (255, 255, 255),
    "blue": (67, 142, 219),
    "red": (219, 37, 37),
}

FACE_CONFIDENCE_THRESHOLD = 0.5
