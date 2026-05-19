import io
import pytest
from PIL import Image
import numpy as np


@pytest.fixture
def sample_face_image():
    """Create a simple test image with a face-like pattern."""
    img = Image.new("RGB", (400, 400), color=(200, 180, 160))
    pixels = np.array(img)
    # Draw a simple face-like oval
    center_x, center_y = 200, 180
    for y in range(400):
        for x in range(400):
            dist = ((x - center_x) ** 2 / 80**2) + ((y - center_y) ** 2 / 100**2)
            if dist < 1:
                pixels[y, x] = [180, 150, 130]
    img = Image.fromarray(pixels)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf


@pytest.fixture
def sample_no_face_image():
    """Create a test image without any face."""
    img = Image.new("RGB", (400, 400), color=(100, 200, 100))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf


@pytest.fixture
def sample_multi_face_image():
    """Create a test image with multiple face-like patterns."""
    img = Image.new("RGB", (800, 400), color=(200, 180, 160))
    pixels = np.array(img)
    # Draw two face-like ovals
    for cx, cy in [(200, 180), (600, 180)]:
        for y in range(400):
            for x in range(800):
                dist = ((x - cx) ** 2 / 80**2) + ((y - cy) ** 2 / 100**2)
                if dist < 1:
                    pixels[y, x] = [180, 150, 130]
    img = Image.fromarray(pixels)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf


@pytest.fixture
def sample_simple_bg_image():
    """Create a test image with a simple solid background."""
    img = Image.new("RGB", (400, 400), color=(255, 255, 255))
    pixels = np.array(img)
    # Add a simple shape in the center
    pixels[100:300, 100:300] = [180, 150, 130]
    img = Image.fromarray(pixels)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


@pytest.fixture
def sample_complex_bg_image():
    """Create a test image with a complex background."""
    img = Image.new("RGB", (400, 400), color=(50, 100, 150))
    pixels = np.array(img)
    # Add gradient background
    for y in range(400):
        for x in range(400):
            pixels[y, x] = [50 + x // 4, 100 + y // 4, 150 - x // 8]
    # Add a shape
    pixels[100:300, 100:300] = [180, 150, 130]
    img = Image.fromarray(pixels)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


@pytest.fixture
def photo_sizes():
    """Return supported photo sizes."""
    return {
        "1inch": (295, 413),
        "2inch": (413, 579),
        "small_1inch": (260, 378),
        "passport": (390, 567),
    }
