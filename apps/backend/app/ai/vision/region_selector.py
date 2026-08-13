"""Region Selector extracts rectangular focus regions from viewports.
"""

from typing import List, Optional, Tuple
from PIL import Image
from app.ai.vision.models import ScreenRegion

class RegionSelector:
    """Focuses visual operations to target screen quadrants or windows."""

    def select_rectangle(self, image: Image.Image, x: int, y: int, w: int, h: int) -> Image.Image:
        """Returns cropped image corresponding to rectangular parameters."""
        # Ensure values fit within image boundaries
        left = max(0, min(x, image.width - 1))
        top = max(0, min(y, image.height - 1))
        right = max(left + 1, min(x + w, image.width))
        bottom = max(top + 1, min(y + h, image.height))
        
        return image.crop((left, top, right, bottom))

    def select_active_window(self, image: Image.Image, window_bounds: Tuple[int, int, int, int]) -> Image.Image:
        """Crops image to window-specific bounds."""
        x, y, w, h = window_bounds
        return self.select_rectangle(image, x, y, w, h)

    def select_polygon(self, image: Image.Image, vertices: List[Tuple[int, int]]) -> Image.Image:
        """Crops matching bounding box of polygon vertices."""
        if not vertices:
            return image
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        return self.select_rectangle(image, min_x, min_y, max_x - min_x, max_y - min_y)
