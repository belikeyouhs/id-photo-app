import re
import uuid
from pathlib import Path

import cv2
import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from PIL import Image

from ..config import ALLOWED_EXTENSIONS, BG_COLORS, MAX_FILE_SIZE, MAX_IMAGE_DIMENSION, OUTPUT_DIR, PHOTO_SIZES
from ..models.schemas import (
    ErrorResponse,
    PhotoDimensions,
    PhotoGenerateData,
    PhotoGenerateResponse,
    PhotoSizeInfo,
    PhotoSizeListResponse,
)
from ..services.background import process_background
from ..services.crop import smart_crop
from ..services.face_detector import face_detector

router = APIRouter(prefix="/api/photo", tags=["photo"])


def _validate_upload(file: UploadFile, content: bytes) -> None:
    if file.content_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(error="INVALID_FORMAT", message="仅支持 JPEG 和 PNG 格式").model_dump(),
        )
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(error="FILE_TOO_LARGE", message="文件大小不能超过 10MB").model_dump(),
        )


def _preprocess_image(image: np.ndarray) -> np.ndarray:
    h, w = image.shape[:2]
    if max(h, w) > MAX_IMAGE_DIMENSION:
        scale = MAX_IMAGE_DIMENSION / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return image


@router.post("/generate", response_model=PhotoGenerateResponse)
async def generate_photo(
    file: UploadFile = File(...),
    size: str = Form("1inch"),
    bg_color: str = Form("white"),
):
    content = await file.read()
    _validate_upload(file, content)

    if size not in PHOTO_SIZES:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(error="INVALID_SIZE", message=f"不支持的尺寸: {size}").model_dump(),
        )
    if bg_color in BG_COLORS:
        bg_rgb = BG_COLORS[bg_color]
    elif re.fullmatch(r"#[0-9a-fA-F]{6}", bg_color):
        bg_rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
    else:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(error="INVALID_BG_COLOR", message=f"不支持的背景色: {bg_color}").model_dump(),
        )

    nparr = np.frombuffer(content, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(error="INVALID_IMAGE", message="无法解析图片").model_dump(),
        )

    image = _preprocess_image(image)

    face = face_detector.detect_primary_face(image)
    if face is None:
        return PhotoGenerateResponse(
            success=False,
            error="NO_FACE_DETECTED",
            message="未检测到人脸，请上传包含清晰人脸的照片",
        )

    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    processed = process_background(pil_image, bg_rgb)

    size_info = PHOTO_SIZES[size]
    result = smart_crop(processed, face["bbox"], size_info["width"], size_info["height"])

    photo_id = uuid.uuid4().hex[:12]
    output_path = OUTPUT_DIR / f"{photo_id}.png"
    result.save(str(output_path), "PNG")

    return PhotoGenerateResponse(
        success=True,
        data=PhotoGenerateData(
            photo_id=photo_id,
            photo_url=f"/api/photo/download/{photo_id}",
            face_detected=True,
            confidence=round(face["confidence"], 2),
            size=size,
            dimensions=PhotoDimensions(width=size_info["width"], height=size_info["height"]),
        ),
    )


@router.get("/download/{photo_id}")
async def download_photo(photo_id: str):
    if not re.fullmatch(r"[0-9a-f]{1,32}", photo_id):
        raise HTTPException(status_code=400, detail=ErrorResponse(error="INVALID_ID", message="无效的照片 ID").model_dump())
    file_path = OUTPUT_DIR / f"{photo_id}.png"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=ErrorResponse(error="NOT_FOUND", message="照片不存在").model_dump())
    return FileResponse(str(file_path), media_type="image/png", filename=f"{photo_id}.png")


@router.get("/sizes", response_model=PhotoSizeListResponse)
async def list_sizes():
    sizes = [
        PhotoSizeInfo(key=key, name=info["name"], width=info["width"], height=info["height"], mm=info["mm"])
        for key, info in PHOTO_SIZES.items()
    ]
    return PhotoSizeListResponse(success=True, data=sizes)
