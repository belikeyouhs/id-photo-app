import numpy as np
from PIL import Image
from rembg import remove


def remove_background(image: Image.Image) -> Image.Image:
    return remove(image)


def replace_background(foreground: Image.Image, bg_color: tuple[int, int, int]) -> Image.Image:
    if foreground.mode != "RGBA":
        foreground = foreground.convert("RGBA")

    background = Image.new("RGBA", foreground.size, (*bg_color, 255))
    composite = Image.alpha_composite(background, foreground)
    return composite.convert("RGB")


def process_background(image: Image.Image, bg_color: tuple[int, int, int]) -> Image.Image:
    fg = remove_background(image)
    return replace_background(fg, bg_color)
