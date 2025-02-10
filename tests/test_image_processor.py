# tests/test_image_processor.py
import os
import sys
import pytest
from unittest.mock import Mock, patch
import requests
from PIL import Image
from io import BytesIO

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.utils.image_processor import ImageProcessor


@pytest.fixture
def image_processor(test_image_dirs):
    raw_dir, processed_dir = test_image_dirs
    session = requests.Session()
    return ImageProcessor(raw_dir, processed_dir, session)


@pytest.fixture
def sample_image():
    """Create a sample test image."""
    img = Image.new("RGB", (800, 600), color="red")
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format="JPEG")
    img_byte_arr.seek(0)
    return img_byte_arr.getvalue()


def test_sanitize_filename(image_processor):
    """Test filename sanitization."""
    test_cases = [
        ("Hello World!", "Hello_World"),
        ("test/file:name", "test_file_name"),
        ("test\\file", "test_file"),
        ("   spaces   ", "spaces"),
        ("!@#$%^&*()", ""),
    ]

    for input_name, expected in test_cases:
        assert image_processor.sanitize_filename(input_name) == expected
