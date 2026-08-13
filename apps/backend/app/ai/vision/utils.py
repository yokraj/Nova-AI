"""Utility operations for the Vision Engine.
"""

import base64
import io
import hashlib
from typing import Any, Dict
from PIL import Image

def image_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
    """Converts a PIL Image object into raw compressed bytes."""
    output = io.BytesIO()
    image.save(output, format=format)
    return output.getvalue()

def bytes_to_image(image_bytes: bytes) -> Image.Image:
    """Creates a PIL Image object from raw compressed bytes."""
    return Image.open(io.BytesIO(image_bytes))

def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """Converts a PIL Image object into a base64 encoded string."""
    image_bytes = image_to_bytes(image, format=format)
    return base64.b64encode(image_bytes).decode("utf-8")

def base64_to_image(base64_str: str) -> Image.Image:
    """Decodes a base64 encoded string into a PIL Image."""
    image_bytes = base64.b64decode(base64_str)
    return bytes_to_image(image_bytes)

def calculate_image_hash(image: Image.Image) -> str:
    """Computes a SHA-256 hash of the raw image bytes to serve as a cache key."""
    img_bytes = image_to_bytes(image)
    return hashlib.sha256(img_bytes).hexdigest()
