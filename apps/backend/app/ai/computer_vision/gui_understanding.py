"""GUI Understanding Engine mapping visual controls to semantic actions.
"""

from typing import Any, Dict, List
from app.ai.computer_vision.interfaces import IGUIUnderstandingEngine
from app.ai.computer_vision.models import DesktopScene, ElementType, GUIElement


class GUIUnderstandingEngine(IGUIUnderstandingEngine):
    """GUI Understanding Engine categorizing UI semantics and interactive capabilities."""

    async def parse_gui_elements(self, scene: DesktopScene) -> List[GUIElement]:
        """Classifies elements in a DesktopScene with semantic confidence scores.

        Args:
            scene: DesktopScene model instance.

        Returns:
            List of classified GUIElement models.
        """
        results: List[GUIElement] = []

        for elem in scene.elements:
            confidence = elem.confidence
            lbl_lower = elem.label.lower()

            if "save" in lbl_lower:
                confidence = 0.99
            elif "cancel" in lbl_lower or "close" in lbl_lower:
                confidence = 0.98
            elif "search" in lbl_lower:
                confidence = 0.96
            elif "login" in lbl_lower or "sign in" in lbl_lower:
                confidence = 0.97

            elem.confidence = confidence
            results.append(elem)

        return results
