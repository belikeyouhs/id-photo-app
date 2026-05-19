from pydantic import BaseModel
from typing import Optional


class PhotoGenerateRequest(BaseModel):
    size: str = "1inch"
    bg_color: str = "white"


class PhotoDimensions(BaseModel):
    width: int
    height: int


class PhotoGenerateData(BaseModel):
    photo_id: str
    photo_url: str
    face_detected: bool
    confidence: float
    size: str
    dimensions: PhotoDimensions


class PhotoGenerateResponse(BaseModel):
    success: bool
    data: Optional[PhotoGenerateData] = None
    error: Optional[str] = None
    message: Optional[str] = None


class PhotoSizeInfo(BaseModel):
    key: str
    name: str
    width: int
    height: int
    mm: str


class PhotoSizeListResponse(BaseModel):
    success: bool
    data: list[PhotoSizeInfo]


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str
