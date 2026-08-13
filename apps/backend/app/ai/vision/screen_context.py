"""Screen Context stores layout nodes and extracted active UI structures.
"""

from typing import List, Optional
from app.ai.vision.models import UIElement, LayoutNode, ColorPalette, BoundingBox

class ScreenContext:
    """Holds active UI tree and extracted visual descriptors for the current view."""

    def __init__(
        self,
        elements: Optional[List[UIElement]] = None,
        layout_root: Optional[LayoutNode] = None,
        colors: Optional[ColorPalette] = None
    ) -> None:
        self.elements = elements or []
        self.layout_root = layout_root
        self.colors = colors

    def find_elements_by_type(self, element_type: str) -> List[UIElement]:
        """Finds all UI controls matching target type (e.g. 'button')."""
        return [el for el in self.elements if el.type.lower() == element_type.lower()]

    def find_element_by_label(self, label: str) -> Optional[UIElement]:
        """Finds element matching target text search."""
        for el in self.elements:
            if el.label and label.lower() in el.label.lower():
                return el
        return None
