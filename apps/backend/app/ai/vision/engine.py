"""LocalVisionEngine orchestrates the 12-stage visual analysis pipeline.
"""

import time
from typing import Optional, Any
from PIL import Image

from app.ai.gateway import AIGateway
from app.ai.vision.configuration import VisionConfiguration
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
from app.ai.vision.screenshot_manager import ScreenshotManager
from app.ai.vision.ocr_engine import OCREngine
from app.ai.vision.ui_detector import UIDetector
from app.ai.vision.object_detector import ObjectDetector
from app.ai.vision.layout_analyzer import LayoutAnalyzer
from app.ai.vision.color_analyzer import ColorAnalyzer
from app.ai.vision.context_builder import ContextBuilder
from app.ai.vision.action_planner import ActionPlanner
from app.ai.vision.memory import VisionMemory
from app.ai.vision.metrics import VisionMetricsTracker
from app.ai.vision.cache import VisionCache
from app.ai.vision.providers.local_cv import LocalCVProvider
from app.ai.vision.providers.mock_provider import MockVisionProvider
from app.ai.vision.providers.ollama_vision import OllamaVisionProvider

class LocalVisionEngine:
    """Consolidates visual sub-modules into a production-ready vision orchestrator."""

    def __init__(
        self,
        config: Optional[VisionConfiguration] = None,
        gateway: Optional[AIGateway] = None,
        memory_engine: Optional[Any] = None
    ) -> None:
        self.config = config or VisionConfiguration()
        self.gateway = gateway
        
        # Sub-components
        self.loader = ImageLoader()
        self.processor = ImageProcessor()
        self.screenshot_mgr = ScreenshotManager()
        self.ocr_engine = OCREngine()
        self.ui_detector = UIDetector()
        self.object_detector = ObjectDetector()
        self.layout_analyzer = LayoutAnalyzer()
        self.color_analyzer = ColorAnalyzer()
        self.context_builder = ContextBuilder()
        self.planner = ActionPlanner()
        self.memory = VisionMemory(memory_engine)
        self.metrics_tracker = VisionMetricsTracker()
        self.cache = VisionCache()

        # Load target provider
        if self.config.provider == "ollama_vision":
            self.provider = OllamaVisionProvider()
        elif self.config.provider == "mock":
            self.provider = MockVisionProvider()
        else:
            self.provider = LocalCVProvider()

    async def analyze_screen(self, request: VisionRequest) -> VisionResponse:
        """Executes the full 12-stage visual reasoning pipeline."""
        self.metrics_tracker.reset()
        self.metrics_tracker.start_stage("total")

        # Stage 1: Load image or Stage 2: Capture screenshot
        self.metrics_tracker.start_stage("load")
        if request.image_bytes or request.image_path:
            img = self.loader.load(request.image_path, request.image_bytes)
        else:
            # Capture active viewport
            if request.region:
                from app.ai.vision.models import ScreenRegion
                region = ScreenRegion(
                    x=request.region.x,
                    y=request.region.y,
                    width=request.region.width,
                    height=request.region.height
                )
                img = self.screenshot_mgr.capture_region(region)
            else:
                img = self.screenshot_mgr.capture_screen()
        self.metrics_tracker.end_stage("load")

        # Check Cache
        if self.config.image_cache_enabled:
            cached = self.cache.get(img, "analysis")
            if cached:
                self.metrics_tracker.end_stage("total")
                return cached

        # Stage 3: Preprocess image
        self.metrics_tracker.start_stage("preprocess")
        img_processed = self.processor.preprocess(img, self.config.cv.max_image_size)
        self.metrics_tracker.end_stage("preprocess")

        # Stage 4: OCR
        self.metrics_tracker.start_stage("ocr")
        ocr_result = await self.ocr_engine.detect_text(img_processed)
        self.metrics_tracker.end_stage("ocr")

        # Stage 5: Detect UI Elements
        self.metrics_tracker.start_stage("detection")
        elements = self.ui_detector.detect_elements(img_processed, self.config.confidence_threshold)
        
        # Stage 6: Detect objects
        objects = self.object_detector.detect_objects(img_processed, self.config.confidence_threshold)
        self.metrics_tracker.end_stage("detection")

        # Stage 7: Analyze layout
        layout_root = self.layout_analyzer.analyze_layout(elements, img_processed.size)

        # Stage 8: Analyze colors
        colors = self.color_analyzer.analyze_colors(img_processed)

        # Stage 9: Build screen context
        screen_context = self.context_builder.build_context(
            elements=elements,
            layout_root=layout_root,
            colors=colors,
            ocr=ocr_result,
            objects=objects
        )

        # Stage 10: Store memory
        summary = f"Desktop UI view with {len(elements)} elements, {colors.theme} theme."
        layout_desc = f"Root: {layout_root.name} containing {len(layout_root.children)} nodes."
        await self.memory.store_observation(summary, ocr_result.full_text, layout_desc)

        # Stage 11: Generate action plan
        action_plan = self.planner.plan_login_sequence(elements)

        # Tracing metrics
        self.metrics_tracker.end_stage("total")
        timings = self.metrics_tracker.get_metrics()
        
        metrics = VisionMetrics(
            load_time=timings.get("load", 0.0),
            preprocessing_time=timings.get("preprocess", 0.0),
            ocr_time=timings.get("ocr", 0.0),
            detection_time=timings.get("detection", 0.0),
            pipeline_time=timings.get("total", 0.0)
        )

        response = VisionResponse(
            status="success",
            metadata=self.screenshot_mgr.generate_metadata(img_processed),
            analysis=ScreenAnalysis(
                elements=elements,
                objects=objects,
                layout_root=layout_root
            ),
            ocr=ocr_result,
            colors=colors,
            action_plan=action_plan,
            metrics=metrics
        )

        if self.config.image_cache_enabled:
            self.cache.set(img, "analysis", response)

        return response
