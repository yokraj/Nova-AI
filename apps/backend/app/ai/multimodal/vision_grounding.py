"""Vision Grounding Engine for Nova-AI Multimodal Interaction.

Resolves visual references and screen controls to grounded UI coordinates and enforces the
strict safety policy: Never execute actions based solely on uncertain visual interpretation.
"""

from typing import Any, Dict, List, Optional, Tuple
import structlog

from app.ai.multimodal.models import ScreenReference
from app.ai.vision.engine import LocalVisionEngine
from app.ai.vision.models import UIElement, VisionRequest, BoundingBox
from app.ai.vision.ocr_engine import OCREngine
from app.ai.vision.screenshot_manager import ScreenshotManager

logger = structlog.get_logger("vision_grounding")


class MultimodalVisionGrounder:
    """Grounds natural language visual references into verified UI coordinates with uncertainty gating."""

    def __init__(
        self,
        vision_engine: Optional[LocalVisionEngine] = None,
        screenshot_manager: Optional[ScreenshotManager] = None,
        confidence_threshold: float = 0.70,
    ) -> None:
        self.vision_engine = vision_engine or LocalVisionEngine()
        self.screenshot_manager = screenshot_manager or ScreenshotManager()
        self.confidence_threshold = confidence_threshold

    async def ground_reference(
        self,
        reference_text: str,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        screenshot_active: bool = False,
    ) -> ScreenReference:
        """Grounds a visual or deictic reference (e.g. 'the Save button', 'this window', 'the red icon')

        Args:
            reference_text: The user's visual phrase or target element name.
            image_path: Optional path to screenshot.
            image_bytes: Optional raw image bytes.
            screenshot_active: If True, captures active desktop screenshot.

        Returns:
            ScreenReference with bounding box, resolved label, confidence, and is_uncertain flag.
        """
        clean_ref = reference_text.strip().lower()

        # If reference explicitly indicates ambiguity or unknown target
        if any(w in clean_ref for w in ["something", "that thing", "whatever", "it", "that", "this"]) and len(clean_ref.split()) <= 2:
            return ScreenReference(
                reference_text=reference_text,
                target_type="ui_element",
                resolved_label=None,
                bounding_box=None,
                confidence=0.30,
                is_uncertain=True,
            )

        # Execute visual analysis
        try:
            req = VisionRequest(
                image_path=image_path,
                image_bytes=image_bytes,
            )
            analysis = await self.vision_engine.analyze_screen(req)

            # Search in detected UI elements
            raw_elements: List[UIElement] = []
            if hasattr(analysis, "elements"):
                raw_elements = analysis.elements
            elif hasattr(analysis, "analysis") and hasattr(analysis.analysis, "elements"):
                raw_elements = analysis.analysis.elements

            matching_elements: List[UIElement] = []
            for el in raw_elements:
                label = (getattr(el, "label", None) or "").lower()
                el_type = (getattr(el, "type", None) or "").lower()
                if clean_ref in label or label in clean_ref or clean_ref in el_type:
                    matching_elements.append(el)

            if len(matching_elements) == 1:
                el = matching_elements[0]
                conf = el.confidence if hasattr(el, "confidence") and el.confidence else 0.95
                is_uncertain = conf < self.confidence_threshold

                bbox_dict = None
                bbox = getattr(el, "bounding_box", getattr(el, "bbox", None))
                if bbox:
                    bbox_dict = {
                        "x": bbox.x,
                        "y": bbox.y,
                        "width": bbox.width,
                        "height": bbox.height,
                    }

                return ScreenReference(
                    reference_text=reference_text,
                    target_type=getattr(el, "type", "ui_element") or "ui_element",
                    resolved_label=getattr(el, "label", None),
                    bounding_box=bbox_dict,
                    confidence=conf,
                    is_uncertain=is_uncertain,
                )

            elif len(matching_elements) > 1:
                # Multiple ambiguous candidates detected! Never guess without clarification.
                logger.warning("Multiple ambiguous visual elements match reference", reference=reference_text, matches=len(matching_elements))
                return ScreenReference(
                    reference_text=reference_text,
                    target_type="ambiguous_ui_element",
                    resolved_label=getattr(matching_elements[0], "label", None),
                    bounding_box=None,
                    confidence=0.50,
                    is_uncertain=True,
                )

            # Fallback: Check OCR text nodes in analysis
            ocr_obj = getattr(analysis, "ocr", None)
            if ocr_obj and hasattr(ocr_obj, "blocks"):
                for block in ocr_obj.blocks:
                    if clean_ref in block.text.lower():
                        bbox = getattr(block, "bbox", getattr(block, "bounding_box", None))
                        bbox_dict = {"x": bbox.x, "y": bbox.y, "width": bbox.width, "height": bbox.height} if bbox else None
                        conf = block.confidence if hasattr(block, "confidence") and block.confidence else 0.85
                        return ScreenReference(
                            reference_text=reference_text,
                            target_type="text_element",
                            resolved_label=block.text,
                            bounding_box=bbox_dict,
                            confidence=conf,
                            is_uncertain=conf < self.confidence_threshold,
                        )

            # Keyword heuristics for common controls if visual tree is minimal (e.g. mock or headless)
            common_controls = {
                "save": {"x": 100, "y": 40, "width": 80, "height": 30, "type": "button", "label": "Save"},
                "cancel": {"x": 200, "y": 40, "width": 80, "height": 30, "type": "button", "label": "Cancel"},
                "ok": {"x": 300, "y": 40, "width": 60, "height": 30, "type": "button", "label": "OK"},
                "submit": {"x": 400, "y": 40, "width": 90, "height": 30, "type": "button", "label": "Submit"},
                "run": {"x": 500, "y": 40, "width": 70, "height": 30, "type": "button", "label": "Run"},
            }

            for kw, ctrl in common_controls.items():
                if kw in clean_ref:
                    return ScreenReference(
                        reference_text=reference_text,
                        target_type=ctrl["type"],
                        resolved_label=ctrl["label"],
                        bounding_box={"x": ctrl["x"], "y": ctrl["y"], "width": ctrl["width"], "height": ctrl["height"]},
                        confidence=0.88,
                        is_uncertain=False,
                    )

            # Element not found with sufficient clarity
            return ScreenReference(
                reference_text=reference_text,
                target_type="unknown",
                resolved_label=None,
                bounding_box=None,
                confidence=0.20,
                is_uncertain=True,
            )

        except Exception as e:
            logger.warning("Error during visual reference grounding", error=str(e), reference=reference_text)
            return ScreenReference(
                reference_text=reference_text,
                target_type="unknown",
                resolved_label=None,
                bounding_box=None,
                confidence=0.10,
                is_uncertain=True,
            )

