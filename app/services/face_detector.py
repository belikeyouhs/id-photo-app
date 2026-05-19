import cv2
import numpy as np
from pathlib import Path

from ..config import FACE_CONFIDENCE_THRESHOLD


class FaceDetector:
    def __init__(self):
        model_dir = Path(__file__).parent.parent / "models"
        proto_path = model_dir / "deploy.prototxt"
        model_path = model_dir / "res10_300x300_ssd_iter_140000.caffemodel"

        if proto_path.exists() and model_path.exists():
            self.net = cv2.dnn.readNetFromCaffe(str(proto_path), str(model_path))
        else:
            self.net = None

        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.haar_cascade = cv2.CascadeClassifier(cascade_path)

    def detect(self, image: np.ndarray) -> list[dict]:
        if self.net is None:
            return self._detect_haar(image)

        h, w = image.shape[:2]
        blob = cv2.dnn.blobFromImage(
            cv2.resize(image, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0)
        )
        self.net.setInput(blob)
        detections = self.net.forward()

        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence < FACE_CONFIDENCE_THRESHOLD:
                continue

            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            x1, y1, x2, y2 = box.astype(int)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            if x2 > x1 and y2 > y1:
                faces.append({
                    "bbox": (x1, y1, x2, y2),
                    "confidence": float(confidence),
                })

        faces.sort(key=lambda f: f["confidence"], reverse=True)
        return faces

    def _detect_haar(self, image: np.ndarray) -> list[dict]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        rects = self.haar_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        faces = []
        for (x, y, w, h) in rects:
            faces.append({
                "bbox": (x, y, x + w, y + h),
                "confidence": 0.9,
            })
        return faces

    def detect_primary_face(self, image: np.ndarray) -> dict | None:
        faces = self.detect(image)
        if not faces:
            return None
        return max(faces, key=lambda f: (f["bbox"][2] - f["bbox"][0]) * (f["bbox"][3] - f["bbox"][1]))


face_detector = FaceDetector()
