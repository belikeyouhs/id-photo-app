from PIL import Image
import numpy as np


def smart_crop(
    image: Image.Image,
    face_bbox: tuple[int, int, int, int],
    target_width: int,
    target_height: int,
) -> Image.Image:
    img_w, img_h = image.size
    x1, y1, x2, y2 = face_bbox

    face_cx = (x1 + x2) / 2
    face_cy = (y1 + y2) / 2
    face_h = y2 - y1

    if target_width <= 0 or target_height <= 0:
        raise ValueError(f"Invalid target dimensions: {target_width}x{target_height}")

    target_ratio = target_width / target_height

    crop_h = int(face_h * 3.0)
    crop_h = min(crop_h, img_h)
    crop_w = int(crop_h * target_ratio)
    crop_w = min(crop_w, img_w)
    crop_h = int(crop_w / target_ratio)

    center_x = int(face_cx)
    center_y = int(face_cy - face_h * 0.3)

    half_w = crop_w // 2
    half_h = crop_h // 2

    left = center_x - half_w
    top = center_y - half_h
    right = left + crop_w
    bottom = top + crop_h

    if left < 0:
        right -= left
        left = 0
    if top < 0:
        bottom -= top
        top = 0
    if right > img_w:
        left -= right - img_w
        right = img_w
    if bottom > img_h:
        top -= bottom - img_h
        bottom = img_h

    left = max(0, left)
    top = max(0, top)
    right = min(img_w, right)
    bottom = min(img_h, bottom)

    cropped = image.crop((left, top, right, bottom))
    return cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)
