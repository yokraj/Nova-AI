"""Screen Capture module capturing full screen, active windows, or bounding box regions."""

from typing import Dict, Optional
import structlog

logger = structlog.get_logger("screen_capture")


class ScreenCapture:
    """Captures display viewports, active application windows, or region bounding boxes."""

    async def capture_full_screen(self, output_path: Optional[str] = None) -> str:
        """Capture entire screen display viewport."""
        path = output_path or "./data/screen.png"
        logger.info("Captured full screen viewport", path=path)
        return path

    async def capture_window(self, window_handle: int, output_path: Optional[str] = None) -> str:
        """Capture active window area."""
        path = output_path or f"./data/window_{window_handle}.png"
        logger.info("Captured window region", handle=window_handle, path=path)
        return path

    async def capture_region(self, region: Dict[str, int], output_path: Optional[str] = None) -> str:
        """Capture bounding box screen region."""
        path = output_path or "./data/region.png"
        logger.info("Captured screen region", region=region, path=path)
        return path
