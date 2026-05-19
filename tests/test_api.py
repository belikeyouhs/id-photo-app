import io
import pytest
from PIL import Image
import numpy as np
from unittest.mock import patch


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from httpx import AsyncClient, ASGITransport
    from app.main import app

    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.fixture
def valid_image_bytes():
    """Create a valid JPEG image as bytes."""
    img = Image.new("RGB", (400, 400), color=(200, 180, 160))
    pixels = np.array(img)
    # Add face-like pattern
    for y in range(150, 250):
        for x in range(150, 250):
            pixels[y, x] = [180, 150, 130]
    img = Image.fromarray(pixels)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def png_image_bytes():
    """Create a valid PNG image as bytes."""
    img = Image.new("RGBA", (400, 400), color=(200, 180, 160, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def oversized_image_bytes():
    """Create an image larger than 10MB."""
    target_size = 10 * 1024 * 1024 + 1024
    rng = np.random.RandomState(42)
    data = rng.randint(0, 256, size=target_size, dtype=np.uint8).tobytes()
    return data


@pytest.fixture
def mock_face_detector():
    """Mock face detector to return a valid face."""
    with patch('app.routers.photo.face_detector') as mock:
        mock.detect_primary_face.return_value = {
            "bbox": (100, 80, 300, 320),
            "confidence": 0.95,
        }
        yield mock


@pytest.fixture
def mock_background():
    """Mock background processing to return a simple image."""
    with patch('app.routers.photo.process_background') as mock:
        def fake_process(image, color):
            return Image.new("RGB", image.size, color)
        mock.side_effect = fake_process
        yield mock


class TestPhotoGenerateAPI:
    """Integration tests for POST /api/photo/generate."""

    @pytest.mark.asyncio
    async def test_generate_with_valid_image(self, client, valid_image_bytes, mock_face_detector, mock_background):
        """正常流程：上传有效图片应返回处理结果。"""
        async with client:
            response = await client.post(
                "/api/photo/generate",
                files={"file": ("test.jpg", valid_image_bytes, "image/jpeg")},
                data={"size": "1inch", "bg_color": "white"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "photo_id" in data["data"]
        assert "photo_url" in data["data"]

    @pytest.mark.asyncio
    async def test_generate_with_different_sizes(self, client, valid_image_bytes, mock_face_detector, mock_background):
        """不同尺寸参数应正常处理。"""
        sizes = ["1inch", "2inch", "small_1inch", "passport"]
        async with client:
            for size in sizes:
                response = await client.post(
                    "/api/photo/generate",
                    files={"file": ("test.jpg", valid_image_bytes, "image/jpeg")},
                    data={"size": size, "bg_color": "white"},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_generate_with_different_bg_colors(self, client, valid_image_bytes, mock_face_detector, mock_background):
        """不同背景色参数应正常处理。"""
        colors = ["white", "blue", "red"]
        async with client:
            for color in colors:
                response = await client.post(
                    "/api/photo/generate",
                    files={"file": ("test.jpg", valid_image_bytes, "image/jpeg")},
                    data={"size": "1inch", "bg_color": color},
                )
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_generate_with_png_image(self, client, png_image_bytes, mock_face_detector, mock_background):
        """PNG 格式图片应正常处理。"""
        async with client:
            response = await client.post(
                "/api/photo/generate",
                files={"file": ("test.png", png_image_bytes, "image/png")},
                data={"size": "1inch", "bg_color": "white"},
            )

        assert response.status_code == 200


class TestPhotoGenerateErrors:
    """Error scenario tests for POST /api/photo/generate."""

    @pytest.mark.asyncio
    async def test_no_image_returns_422(self, client):
        """无图片上传应返回 422。"""
        async with client:
            response = await client.post(
                "/api/photo/generate",
                data={"size": "1inch", "bg_color": "white"},
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_format_returns_400(self, client):
        """非图片格式应返回 400。"""
        fake_file = b"this is not an image"
        async with client:
            response = await client.post(
                "/api/photo/generate",
                files={"file": ("test.txt", fake_file, "text/plain")},
                data={"size": "1inch", "bg_color": "white"},
            )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_oversized_file_returns_400(self, client, oversized_image_bytes):
        """超大文件应返回 400。"""
        async with client:
            response = await client.post(
                "/api/photo/generate",
                files={"file": ("large.jpg", oversized_image_bytes, "image/jpeg")},
                data={"size": "1inch", "bg_color": "white"},
            )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_no_face_returns_error(self, client, valid_image_bytes):
        """无人脸图片应返回 success=False 和 NO_FACE_DETECTED 错误。"""
        with patch('app.routers.photo.face_detector') as mock_detector:
            mock_detector.detect_primary_face.return_value = None

            async with client:
                response = await client.post(
                    "/api/photo/generate",
                    files={"file": ("noface.jpg", valid_image_bytes, "image/jpeg")},
                    data={"size": "1inch", "bg_color": "white"},
                )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"] == "NO_FACE_DETECTED"

    @pytest.mark.asyncio
    async def test_invalid_size_returns_400(self, client, valid_image_bytes):
        """无效尺寸参数应返回 400。"""
        async with client:
            response = await client.post(
                "/api/photo/generate",
                files={"file": ("test.jpg", valid_image_bytes, "image/jpeg")},
                data={"size": "invalid_size", "bg_color": "white"},
            )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_invalid_bg_color_returns_400(self, client, valid_image_bytes):
        """无效背景色参数应返回 400。"""
        async with client:
            response = await client.post(
                "/api/photo/generate",
                files={"file": ("test.jpg", valid_image_bytes, "image/jpeg")},
                data={"size": "1inch", "bg_color": "rainbow"},
            )

        assert response.status_code == 400


class TestPhotoDownloadAPI:
    """Integration tests for GET /api/photo/download/{photo_id}."""

    @pytest.mark.asyncio
    async def test_download_returns_image(self, client, valid_image_bytes, mock_face_detector, mock_background):
        """下载接口应返回图片文件。"""
        async with client:
            gen_response = await client.post(
                "/api/photo/generate",
                files={"file": ("test.jpg", valid_image_bytes, "image/jpeg")},
                data={"size": "1inch", "bg_color": "white"},
            )
            assert gen_response.status_code == 200
            gen_data = gen_response.json()
            assert gen_data["success"] is True
            photo_id = gen_data["data"]["photo_id"]

            dl_response = await client.get(f"/api/photo/download/{photo_id}")

        assert dl_response.status_code == 200
        assert dl_response.headers["content-type"].startswith("image/")

    @pytest.mark.asyncio
    async def test_download_nonexistent_returns_404(self, client):
        """下载不存在的照片应返回 404。"""
        async with client:
            response = await client.get("/api/photo/download/000000000000deadbeef0000")

        assert response.status_code == 404


class TestPhotoSizesAPI:
    """Integration tests for GET /api/photo/sizes."""

    @pytest.mark.asyncio
    async def test_sizes_returns_list(self, client):
        """尺寸列表接口应返回支持的尺寸。"""
        async with client:
            response = await client.get("/api/photo/sizes")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))

    @pytest.mark.asyncio
    async def test_sizes_includes_standard_sizes(self, client):
        """应包含标准证件照尺寸。"""
        async with client:
            response = await client.get("/api/photo/sizes")

        assert response.status_code == 200
        data = response.json()
        sizes_str = str(data).lower()
        for size_name in ["1inch", "2inch", "passport"]:
            assert size_name in sizes_str or size_name.replace("inch", "寸") in sizes_str
