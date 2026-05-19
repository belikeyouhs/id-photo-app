import pytest
import numpy as np
from PIL import Image
import io


class TestBackgroundRemoval:
    """Unit tests for background removal service."""

    def test_remove_background_returns_rgba(self, sample_simple_bg_image):
        """移除背景后应返回 RGBA 图片。"""
        from app.services.background import remove_background

        img = Image.open(sample_simple_bg_image)
        result = remove_background(img)

        assert result.mode == "RGBA"
        assert result.size == img.size

    def test_remove_background_has_transparency(self, sample_simple_bg_image):
        """移除背景后应有透明区域。"""
        from app.services.background import remove_background

        img = Image.open(sample_simple_bg_image)
        result = remove_background(img)

        alpha = np.array(result)[:, :, 3]
        assert alpha.min() < 128  # Some transparent pixels

    def test_replace_background_white(self, sample_simple_bg_image):
        """替换为白色背景。"""
        from app.services.background import remove_background, replace_background

        img = Image.open(sample_simple_bg_image)
        fg = remove_background(img)
        result = replace_background(fg, bg_color=(255, 255, 255))

        assert result.mode == "RGB"
        pixels = np.array(result)
        # Check corners are white (background area)
        assert (pixels[0, 0] == [255, 255, 255]).all()

    def test_replace_background_blue(self, sample_simple_bg_image):
        """替换为蓝色背景。"""
        from app.services.background import remove_background, replace_background

        img = Image.open(sample_simple_bg_image)
        fg = remove_background(img)
        result = replace_background(fg, bg_color=(0, 0, 255))

        assert result.mode == "RGB"
        pixels = np.array(result)
        assert (pixels[0, 0] == [0, 0, 255]).all()

    def test_replace_background_red(self, sample_simple_bg_image):
        """替换为红色背景。"""
        from app.services.background import remove_background, replace_background

        img = Image.open(sample_simple_bg_image)
        fg = remove_background(img)
        result = replace_background(fg, bg_color=(255, 0, 0))

        assert result.mode == "RGB"
        pixels = np.array(result)
        assert (pixels[0, 0] == [255, 0, 0]).all()

    def test_preserves_subject(self, sample_simple_bg_image):
        """移除背景时应保留主体。"""
        from app.services.background import remove_background

        img = Image.open(sample_simple_bg_image)
        result = remove_background(img)

        alpha = np.array(result)[:, :, 3]
        # Center of image should be opaque (subject area)
        center_alpha = alpha[200, 200]
        assert center_alpha > 128
