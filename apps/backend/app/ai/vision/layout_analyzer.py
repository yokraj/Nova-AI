"""Layout Analyzer constructs UI nested containment hierarchies.
"""

from typing import List
from app.ai.vision.interfaces import ILayoutAnalyzer
from app.ai.vision.models import UIElement, LayoutNode, BoundingBox

class LayoutAnalyzer(ILayoutAnalyzer):
    """Parses flat coordinates lists and builds tree layout nodes."""

    def analyze_layout(self, elements: List[UIElement], image_size: tuple[int, int]) -> LayoutNode:
        """Determines spatial nesting and groups sub-elements inside parent containers."""
        # Create a root Desktop node
        root = LayoutNode(
            name="Desktop",
            type="desktop",
            bbox=BoundingBox(x=0.0, y=0.0, width=1.0, height=1.0),
            children=[]
        )

        # Look for a main IDE container (e.g. VS Code editor space) or create one
        ide_node = LayoutNode(
            name="VS Code",
            type="application",
            bbox=BoundingBox(x=0.0, y=0.0, width=1.0, height=1.0),
            children=[]
        )
        root.children.append(ide_node)

        # Sort elements by size descending so we can assign children to larger elements (parent containers)
        sorted_elements = sorted(elements, key=lambda el: el.bbox.width * el.bbox.height, reverse=True)

        # Assign elements as child nodes
        for el in sorted_elements:
            # Skip full screen bounds to avoid infinite recursion
            if el.bbox.width >= 0.95 and el.bbox.height >= 0.95:
                continue
            
            node = LayoutNode(
                name=el.label or el.type.capitalize(),
                type=el.type,
                bbox=el.bbox,
                children=[]
            )
            
            # Check if this belongs inside any existing parent container
            placed = False
            for parent in ide_node.children:
                if self._contains(parent.bbox, node.bbox):
                    parent.children.append(node)
                    placed = True
                    break
            
            if not placed:
                ide_node.children.append(node)

        return root

    def _contains(self, parent: BoundingBox, child: BoundingBox) -> bool:
        """Returns True if parent bounding box contains child bounding box."""
        return (
            parent.x <= child.x and
            parent.y <= child.y and
            (parent.x + parent.width) >= (child.x + child.width) and
            (parent.y + parent.height) >= (child.y + child.height)
        )
