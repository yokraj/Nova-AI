"""Image Processor implements filters, grayscale, edge detection, and scaling.
"""

from typing import Optional, List, Dict, Any
from PIL import Image, ImageFilter, ImageOps
from app.ai.vision.interfaces import IImageProcessor

class ImageProcessor(IImageProcessor):
    """Processes images with filters, resizes, and generates histograms."""

    def preprocess(self, image: Image.Image, target_size: Optional[tuple[int, int]] = None) -> Image.Image:
        """Applies default resize and scaling normalization checks."""
        img = image
        if target_size:
            img = self.resize(img, target_size[0], target_size[1])
        return img

    def resize(self, image: Image.Image, width: int, height: int) -> Image.Image:
        """Resizes the target image."""
        return image.resize((width, height), Image.Resampling.LANCZOS)

    def crop(self, image: Image.Image, x: int, y: int, width: int, height: int) -> Image.Image:
        """Crops rectangular coordinates bounds."""
        return image.crop((x, y, x + width, y + height))

    def rotate(self, image: Image.Image, angle: float) -> Image.Image:
        """Rotates the target image by the given angle."""
        return image.rotate(angle)

    def grayscale(self, image: Image.Image) -> Image.Image:
        """Converts the image to grayscale."""
        return ImageOps.grayscale(image)

    def threshold(self, image: Image.Image, threshold: int = 127) -> Image.Image:
        """Applies binary threshold filtering on the target image."""
        gray = self.grayscale(image)
        return gray.point(lambda p: 255 if p > threshold else 0)

    def blur(self, image: Image.Image, radius: float = 2.0) -> Image.Image:
        """Applies Gaussian Blur filtering."""
        return image.filter(ImageFilter.GaussianBlur(radius))

    def sharpen(self, image: Image.Image) -> Image.Image:
        """Applies Sharpen filtering."""
        return image.filter(ImageFilter.SHARPEN)

    def edge_detection(self, image: Image.Image) -> Image.Image:
        """Applies Edge Detection filtering."""
        return image.filter(ImageFilter.FIND_EDGES)

    def generate_histogram(self, image: Image.Image) -> Dict[str, List[int]]:
        """Generates color channel histograms (R, G, B)."""
        hist = image.histogram()
        # For RGB, histogram has 768 elements (256 * 3)
        if len(hist) >= 768:
            return {
                "red": hist[0:256],
                "green": hist[256:512],
                "blue": hist[512:768]
            }
        # Fallback for grayscale
        return {
            "gray": hist[0:256]
        }
