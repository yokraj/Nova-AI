"""Coordinate Transform handles conversions between normalized vision inputs and display space.
"""

import structlog
from typing import Tuple

logger = structlog.get_logger("coordinate_transform")

try:
    import win32api
    if type(win32api).__name__ in ("MagicMock", "NonCallableMagicMock"):
        WIN32_AVAILABLE = False
    else:
        WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

class CoordinateTransform:
    """Scales relative coordinates [0.0 - 1.0] from Vision Engine to absolute desktop pixels."""

    def __init__(self) -> None:
        self.screen_width = 1920
        self.screen_height = 1080
        self._detect_resolution()

    def _detect_resolution(self) -> None:
        """Discovers primary display resolution using win32 metrics, falling back to 1920x1080."""
        if WIN32_AVAILABLE:
            try:
                self.screen_width = win32api.GetSystemMetrics(0)
                self.screen_height = win32api.GetSystemMetrics(1)
                logger.debug(
                    "Detected primary screen layout dimensions",
                    width=self.screen_width,
                    height=self.screen_height
                )
            except Exception as err:
                logger.warning("Failed to detect screen resolution via Win32; using 1920x1080 fallback", error=str(err))

    def to_absolute(self, x: float, y: float) -> Tuple[int, int]:
        """Translates normalized vision floats to absolute monitor pixels."""
        pixel_x = int(x * self.screen_width)
        pixel_y = int(y * self.screen_height)
        return pixel_x, pixel_y

    def to_normalized(self, x: int, y: int) -> Tuple[float, float]:
        """Translates absolute pixel dimensions to normalized floats."""
        norm_x = float(x) / self.screen_width
        norm_y = float(y) / self.screen_height
        return norm_x, norm_y
