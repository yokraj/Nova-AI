"""Health monitoring rules for checking CV / OCR binaries presence.
"""

import sys
import structlog
from typing import Dict, Any

logger = structlog.get_logger("vision_health")

class VisionHealthMonitor:
    """Verifies dependencies availability and local visual subsystems."""

    async def check_health(self) -> Dict[str, Any]:
        """Runs checks to determine component health."""
        has_pil = False
        try:
            from PIL import Image
            has_pil = True
        except ImportError:
            pass

        has_cv2 = False
        try:
            import cv2
            has_cv2 = True
        except ImportError:
            pass

        has_tesseract = False
        try:
            import pytesseract
            # Light command check to ensure binary works
            pytesseract.get_tesseract_version()
            has_tesseract = True
        except Exception:
            pass

        healthy = has_pil  # At minimum, PIL must be loaded to run basic logic.

        status = {
            "healthy": healthy,
            "pillow_available": has_pil,
            "opencv_available": has_cv2,
            "tesseract_available": has_tesseract,
            "python_version": sys.version,
        }

        logger.info("Vision engine health check completed", healthy=healthy, status=status)
        return status
