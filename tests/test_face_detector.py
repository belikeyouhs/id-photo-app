import pytest
import numpy as np
import cv2
from PIL import Image
from unittest.mock import patch
import io


class TestFaceDetector:
    """Unit tests for face detection service."""

    def test_detect_face_returns_bounding_box(self, sample_face_image):
        """正常人脸图片：应返回人脸边界框和置信度。"""
        from app.services.face_detector import FaceDetector

        detector = FaceDetector()
        img = Image.open(sample_face_image)
        img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        with patch.object(detector, '_detect_haar') as mock_haar:
            mock_haar.return_value = [{
                "bbox": (100, 80, 300, 320),
                "confidence": 0.95,
            }]
            detector.net = None
            result = detector.detect(img_np)

        assert result is not None
        assert len(result) > 0
        face = result[0]
        assert "bbox" in face
        assert "confidence" in face
        assert len(face["bbox"]) == 4  # x1, y1, x2, y2
        assert face["confidence"] > 0

    def test_detect_no_face_returns_empty(self, sample_no_face_image):
        """无人脸图片：应返回空列表。"""
        from app.services.face_detector import FaceDetector

        detector = FaceDetector()
        img = Image.open(sample_no_face_image)
        img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        result = detector.detect(img_np)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_detect_multiple_faces_returns_largest(self, sample_multi_face_image):
        """多人脸图片：使用 detect_primary_face 应返回最大人脸。"""
        from app.services.face_detector import FaceDetector

        detector = FaceDetector()
        img = Image.open(sample_multi_face_image)
        img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        with patch.object(detector, '_detect_haar') as mock_haar:
            mock_haar.return_value = [
                {"bbox": (50, 50, 200, 250), "confidence": 0.9},
                {"bbox": (300, 50, 550, 350), "confidence": 0.85},
            ]
            detector.net = None
            result = detector.detect_primary_face(img_np)

        assert result is not None
        assert "bbox" in result
        assert "confidence" in result
        assert result["bbox"] == (300, 50, 550, 350)

    def test_detect_multiple_faces_returns_all(self, sample_multi_face_image):
        """多人脸图片：使用 detect 应返回所有人脸。"""
        from app.services.face_detector import FaceDetector

        detector = FaceDetector()
        img = Image.open(sample_multi_face_image)
        img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        with patch.object(detector, '_detect_haar') as mock_haar:
            mock_haar.return_value = [
                {"bbox": (50, 50, 200, 250), "confidence": 0.9},
                {"bbox": (300, 50, 550, 350), "confidence": 0.85},
            ]
            detector.net = None
            result = detector.detect(img_np)

        assert result is not None
        assert len(result) == 2

    def test_detect_bbox_within_image_bounds(self, sample_face_image):
        """边界框应在图片范围内。"""
        from app.services.face_detector import FaceDetector

        detector = FaceDetector()
        img = Image.open(sample_face_image)
        img_w, img_h = img.size
        img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        with patch.object(detector, '_detect_haar') as mock_haar:
            mock_haar.return_value = [{
                "bbox": (100, 80, 300, 320),
                "confidence": 0.95,
            }]
            detector.net = None
            result = detector.detect(img_np)

        for face in result:
            x1, y1, x2, y2 = face["bbox"]
            assert x1 >= 0
            assert y1 >= 0
            assert x2 <= img_w
            assert y2 <= img_h
            assert x2 > x1
            assert y2 > y1

    def test_detect_confidence_range(self, sample_face_image):
        """置信度应在 0-1 范围内。"""
        from app.services.face_detector import FaceDetector

        detector = FaceDetector()
        img = Image.open(sample_face_image)
        img_np = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        with patch.object(detector, '_detect_haar') as mock_haar:
            mock_haar.return_value = [{
                "bbox": (100, 80, 300, 320),
                "confidence": 0.95,
            }]
            detector.net = None
            result = detector.detect(img_np)

        for face in result:
            assert 0 <= face["confidence"] <= 1
