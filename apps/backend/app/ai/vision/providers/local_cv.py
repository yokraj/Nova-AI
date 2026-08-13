"""Local CV Provider coordinates local OpenCV and Pillow analysis algorithms.
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
)
from app.ai.vision.image_loader import ImageLoader
from app.ai.vision.image_processor import ImageProcessor
from app.ai.vision.ui_detector import UIDetector
from app.ai.vision.object_detector import ObjectDetector
from app.ai.vision.layout_analyzer import LayoutAnalyzer
from app.ai.vision.color_analyzer import ColorAnalyzer
from app.ai.vision.ocr_engine import OCREngine
from app.ai.vision.action_planner import ActionPlanner
from app.ai.vision.context_builder import ContextBuilder

class LocalCVProvider(IVisionProvider):
    """Orchestrates layout detection, OCR, color, and object detection locally."""

    def __init__(self) -> None:
        self.loader = ImageLoader()
        self.processor = ImageProcessor()
        self.ui_detector = UIDetector()
        self.object_detector = ObjectDetector()
        self.layout_analyzer = LayoutAnalyzer()
        self.color_analyzer = ColorAnalyzer()
        self.ocr_engine = OCREngine()
        self.planner = ActionPlanner()
        self.context_builder = ContextBuilder()

    async def analyze_image(self, request: VisionRequest) -> VisionResponse:
        """Processes request image and extracts visual structures."""
        # Load
        img = self.loader.load(request.image_path, request.image_bytes)
        
        # Crop region if specified
        if request.region:
            img = img.crop((
                request.region.x,
                request.region.y,
                request.region.x + request.region.width,
                request.region.y + request.region.height
            ))

        # 1. OCR
        ocr_result = await self.ocr_engine.detect_text(img)

        # 2. UI Elements
        elements = self.ui_detector.detect_elements(img, 0.5)

        # 3. Objects
        objects = self.object_detector.detect_objects(img, 0.5)

        # 4. Layout
        layout_root = self.layout_analyzer.analyze_layout(elements, img.size)

        # 5. Colors
        colors = self.color_analyzer.analyze_colors(img)

        # 6. Action Plan
        action_plan = self.planner.plan_login_sequence(elements)

        metadata = ScreenshotMetadata(
            width=img.width,
            height=img.height,
            format="PNG"
        )

        return VisionResponse(
            status="success",
            metadata=metadata,
            analysis=ScreenAnalysis(
                elements=elements,
                objects=objects,
                layout_root=layout_root
            ),
            ocr=ocr_result,
            colors=colors,
            action_plan=action_plan,
            metrics=VisionMetrics()
        )

    async def describe_screen(self, image: Image.Image) -> str:
        """Returns standard layout details description."""
        ocr_result = await self.ocr_engine.detect_text(image)
        colors = self.color_analyzer.analyze_colors(image)
        return (
            f"Screen description: Detected theme is {colors.theme}. "
            f"Primary dominant colors are {', '.join(colors.dominant_colors[:2])}. "
            f"Extracted visible text headers: '{ocr_result.full_text[:60]}'."
        )
