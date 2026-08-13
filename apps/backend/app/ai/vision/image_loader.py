"""Image Loader handles loading of PIL Images from path or raw bytes.
"""

import io
import os
from typing import Optional
from PIL import Image
from app.ai.vision.exceptions import ImageProcessingError

class ImageLoader:
    """Utility class to read image files safely and return PIL Image instances."""

    def load(self, image_path: Optional[str] = None, image_bytes: Optional[bytes] = None) -> Image.Image:
        """Loads and returns a PIL Image."""
        if image_bytes:
            try:
                return Image.open(io.BytesIO(image_bytes))
            except Exception as e:
                raise ImageProcessingError(f"Failed to parse image from bytes: {str(e)}") from e
        elif image_path:
            if not os.path.exists(image_path):
                raise ImageProcessingError(f"Target image path does not exist: {image_path}")
            try:
                return Image.open(image_path)
            except Exception as e:
                raise ImageProcessingError(f"Failed to open image file '{image_path}': {str(e)}") from e
        else:
            raise ImageProcessingError("Must provide either image_path or image_bytes to load.")
