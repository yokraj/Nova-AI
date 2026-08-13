"""Mock Provider generates deterministic visual descriptions and layout structures.
"""

from PIL import Image
from app.ai.vision.interfaces import IVisionProvider
from app.ai.vision.models import (
    VisionRequest,
    VisionResponse,
    ScreenshotMetadata,
    ScreenAnalysis,
    OCRResult,
    ColorPalette,
    ActionPlan,
    VisionMetrics,
    UIElement,
    BoundingBox,
)

class MockVisionProvider(IVisionProvider):
    """Generates mock static observations without executing local computer vision algorithms."""

    async def analyze_image(self, request: VisionRequest) -> VisionResponse:
        """Simulates end-to-end vision pipeline processing."""
        width = 1920
        height = 1080
        if request.image_bytes:
            # Estimate size
            pass
            
        elements = [
            UIElement(
                type="button",
                label="Login",
                bbox=BoundingBox(x=0.45, y=0.5, width=0.1, height=0.04),
                confidence=0.98
            )
        ]

        return VisionResponse(
            status="success",
            metadata=ScreenshotMetadata(width=width, height=height, format="png"),
            analysis=ScreenAnalysis(elements=elements, objects=[], layout_root=None),
            ocr=OCRResult(blocks=[], full_text="Mock Screen Text", confidence=0.95),
            colors=ColorPalette(dominant_colors=["#1e1e1e"], theme="dark", brightness=50.0, contrast=10.0),
            action_plan=ActionPlan(steps=[], confidence=1.0),
            metrics=VisionMetrics()
        )

    async def describe_screen(self, image: Image.Image) -> str:
        """Returns mock layout summary details description."""
        return "A mock desktop workspace with an IDE displaying a login form."
