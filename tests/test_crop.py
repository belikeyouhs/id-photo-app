import pytest
import numpy as np
from PIL import Image
import io


class TestCropService:
    """Unit tests for photo cropping service."""

    def test_crop_to_1inch_size(self, sample_face_image):
        """裁剪到一寸尺寸 (295×413)。"""
        from app.services.crop import smart_crop

        img = Image.open(sample_face_image)
        face_bbox = (120, 80, 280, 280)  # x1, y1, x2, y2
        result = smart_crop(img, face_bbox, 295, 413)

        assert result.size == (295, 413)

    def test_crop_to_2inch_size(self, sample_face_image):
        """裁剪到二寸尺寸 (413×579)。"""
        from app.services.crop import smart_crop

        img = Image.open(sample_face_image)
        face_bbox = (120, 80, 280, 280)
        result = smart_crop(img, face_bbox, 413, 579)

        assert result.size == (413, 579)

    def test_crop_to_passport_size(self, sample_face_image):
        """裁剪到护照尺寸 (390×567)。"""
        from app.services.crop import smart_crop

        img = Image.open(sample_face_image)
        face_bbox = (120, 80, 280, 280)
        result = smart_crop(img, face_bbox, 390, 567)

        assert result.size == (390, 567)

    def test_crop_to_small_1inch_size(self, sample_face_image):
        """裁剪到小一寸尺寸 (260×378)。"""
        from app.services.crop import smart_crop

        img = Image.open(sample_face_image)
        face_bbox = (120, 80, 280, 280)
        result = smart_crop(img, face_bbox, 260, 378)

        assert result.size == (260, 378)

    def test_crop_face_centered(self, sample_face_image):
        """裁剪后人脸应在图片中心偏上位置。"""
        from app.services.crop import smart_crop

        img = Image.open(sample_face_image)
        face_bbox = (120, 80, 280, 280)
        result = smart_crop(img, face_bbox, 295, 413)

        result_w, result_h = result.size
        assert result_w == 295
        assert result_h == 413

    def test_crop_preserves_aspect_ratio(self, sample_face_image):
        """裁剪应保持目标尺寸的宽高比。"""
        from app.services.crop import smart_crop

        img = Image.open(sample_face_image)
        face_bbox = (120, 80, 280, 280)

        for size_name, (w, h) in [("1inch", (295, 413)), ("2inch", (413, 579))]:
            result = smart_crop(img, face_bbox, w, h)
            expected_ratio = w / h
            actual_ratio = result.size[0] / result.size[1]
            assert abs(actual_ratio - expected_ratio) < 0.01
