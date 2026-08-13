"""Context Builder aggregates elements, OCR, layout, and colors into a single context structure.
"""

from typing import List, Optional
from app.ai.vision.models import UIElement, LayoutNode, ColorPalette, OCRResult, DetectedObject
from app.ai.vision.screen_context import ScreenContext

class ContextBuilder:
    """Consolidates visual sub-module outputs into a structured ScreenContext."""

    def build_context(
        self,
        elements: List[UIElement],
        layout_root: Optional[LayoutNode],
        colors: Optional[ColorPalette],
        ocr: Optional[OCRResult] = None,
        objects: Optional[List[DetectedObject]] = None
    ) -> ScreenContext:
        """Assembles descriptors into an active screen context representation."""
        # Optional: we can inject OCR labels back into UI elements that overlap spatially!
        for el in elements:
            if not el.label and ocr:
                # Find overlapping OCR block text
                overlapping_text = []
                for b in ocr.blocks:
                    if self._overlaps(el.bbox, b.bbox):
                        overlapping_text.append(b.text)
                if overlapping_text:
                    el.label = " ".join(overlapping_text)

        return ScreenContext(
            elements=elements,
            layout_root=layout_root,
            colors=colors
        )

    def _overlaps(self, bbox_a, bbox_b) -> bool:
        """Returns True if two bounding boxes overlap spatially."""
        # Simple overlap check
        a_left, a_right = bbox_a.x, bbox_a.x + bbox_a.width
        a_top, a_bottom = bbox_a.y, bbox_a.y + bbox_a.height
        b_left, b_right = bbox_b.x, bbox_b.x + bbox_b.width
        b_top, b_bottom = bbox_b.y, bbox_b.y + bbox_b.height

        return not (a_right < b_left or a_left > b_right or a_bottom < b_top or a_top > b_bottom)
