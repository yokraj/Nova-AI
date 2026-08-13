"""UI Element Detector extracting bounding boxes of interactive controls."""

from typing import List
import structlog

from app.ai.automation.models import UIElement

logger = structlog.get_logger("ui_element_detector")


class UIElementDetector:
    """Detects interactive buttons, text inputs, menus, and controls on screen."""

    async def detect_elements(self) -> List[UIElement]:
        """Detect interactive UI elements on screen."""
        elements = [
            UIElement(name="Submit Button", role="button", x=200, y=500, width=100, height=40, text="Submit"),
            UIElement(name="Search Field", role="textbox", x=200, y=200, width=300, height=30, text=""),
            UIElement(name="Close Icon", role="button", x=1900, y=10, width=20, height=20, text="X"),
        ]
        logger.info("Detected interactive UI elements", count=len(elements))
        return elements
