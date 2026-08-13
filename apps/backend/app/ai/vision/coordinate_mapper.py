"""Coordinate Mapper scales bounds between normalized and absolute pixel values.
"""

from app.ai.vision.models import BoundingBox

class CoordinateMapper:
    """Helper class to map coordinates between normalized (0-1) and absolute sizes."""

    def to_absolute(self, bbox: BoundingBox, screen_width: int, screen_height: int) -> BoundingBox:
        """Converts normalized (0.0 - 1.0) coordinates to absolute pixel coordinates."""
        return BoundingBox(
            x=bbox.x * screen_width,
            y=bbox.y * screen_height,
            width=bbox.width * screen_width,
            height=bbox.height * screen_height
        )

    def to_normalized(self, bbox: BoundingBox, screen_width: int, screen_height: int) -> BoundingBox:
        """Converts absolute pixel coordinates to normalized (0.0 - 1.0) ratio values."""
        if screen_width == 0 or screen_height == 0:
            return bbox
        return BoundingBox(
            x=bbox.x / screen_width,
            y=bbox.y / screen_height,
            width=bbox.width / screen_width,
            height=bbox.height / screen_height
        )
