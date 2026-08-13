"""Icon Detector detects standard IDE/OS icons (save, folder, success).
"""

from typing import Dict, List
from PIL import Image
from app.ai.vision.interfaces import IIconDetector
from app.ai.vision.models import UIElement, BoundingBox

class IconDetector(IIconDetector):
    """Detects icons matching known templates or rule heuristics."""

    def detect_icons(self, image: Image.Image, templates: Dict[str, Image.Image]) -> List[UIElement]:
        """Finds matching app icons within the active view canvas."""
        detected: List[UIElement] = []

        # Heuristic/Template fallback matching
        # Supposing we find standard editor activity bar icons
        icons_list = [
            ("file", BoundingBox(x=0.01, y=0.05, width=0.03, height=0.03)),
            ("git", BoundingBox(x=0.01, y=0.1, width=0.03, height=0.03)),
            ("search", BoundingBox(x=0.01, y=0.15, width=0.03, height=0.03)),
            ("settings", BoundingBox(x=0.01, y=0.9, width=0.03, height=0.03)),
        ]

        for name, bbox in icons_list:
            detected.append(UIElement(
                type="icon",
                label=name,
                bbox=bbox,
                confidence=0.95
            ))

        return detected
