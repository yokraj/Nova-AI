"""VisionHelper wrapping image analysis and UI parsing helpers.
"""

from typing import Any, Dict, List, Optional
from app.ai.gateway.ai_gateway import AIGateway
from app.agent_sdk.ai.exceptions import VisionError


class VisionHelper:
    """Interface-ready wrappers for vision capability analysis tasks."""

    def __init__(self, gateway: AIGateway) -> None:
        """Initializes VisionHelper.

        Args:
            gateway: Active AIGateway instance.
        """
        self.gateway = gateway

    async def describe_image(self, image_data: bytes, model: Optional[str] = None) -> str:
        """Generates text description of input image bytes.

        Args:
            image_data: Raw image byte array data.
            model: Optional model override.

        Returns:
            Description string.

        Raises:
            VisionError: If input data is empty.
        """
        # TODO: Connect to vision models when supported by AI Gateway.
        if not image_data:
            raise VisionError("Image data cannot be empty.")
        return "Placeholder: Described image content."

    async def analyze_ui(self, image_data: bytes, model: Optional[str] = None) -> Dict[str, Any]:
        """Analyzes a UI screenshot returning positions of clickable buttons and labels.

        Args:
            image_data: UI screenshot image bytes.
            model: Optional model override.

        Returns:
            Dictionary detailing UI element coordinates.

        Raises:
            VisionError: If input data is empty.
        """
        # TODO: Connect to vision models when supported by AI Gateway.
        if not image_data:
            raise VisionError("UI screen image data cannot be empty.")
        return {
            "elements": [
                {"type": "button", "label": "Submit", "box": [100, 200, 150, 300]},
                {"type": "input", "placeholder": "Search", "box": [50, 200, 80, 500]},
            ]
        }

    async def ocr(self, image_data: bytes, model: Optional[str] = None) -> str:
        """Runs Optical Character Recognition extracting text from image.

        Args:
            image_data: Raw text-bearing image bytes.
            model: Optional model override.

        Returns:
            Extracted text string.

        Raises:
            VisionError: If input data is empty.
        """
        # TODO: Connect to vision models when supported by AI Gateway.
        if not image_data:
            raise VisionError("OCR image data cannot be empty.")
        return "Placeholder: Extracted OCR text."

    async def detect_objects(self, image_data: bytes, model: Optional[str] = None) -> List[Dict[str, Any]]:
        """Identifies classes and bounding boxes of objects in image.

        Args:
            image_data: Input image bytes.
            model: Optional model override.

        Returns:
            List of detected object dictionaries.

        Raises:
            VisionError: If input data is empty.
        """
        # TODO: Connect to vision models when supported by AI Gateway.
        if not image_data:
            raise VisionError("Object detection image data cannot be empty.")
        return [{"class": "person", "confidence": 0.98, "box": [10, 10, 100, 100]}]
