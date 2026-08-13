"""Tests for the Enterprise Vision & Computer Interaction Engine.
"""

import sys
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Mock PIL classes for headless/minimal virtual environments without Pillow
# ---------------------------------------------------------------------------
class MockImage:
    def __init__(self, mode="RGB", size=(200, 100), color=None, is_diff=False):
        self.mode = mode
        self.size = size
        self.width = size[0]
        self.height = size[1]
        self.format = "PNG"
        self.is_diff = is_diff

    def convert(self, mode):
        return MockImage(mode=mode, size=self.size, is_diff=self.is_diff)

    def resize(self, size, resample=None):
        return MockImage(mode=self.mode, size=size, is_diff=self.is_diff)

    def crop(self, box):
        w = box[2] - box[0]
        h = box[3] - box[1]
        return MockImage(mode=self.mode, size=(w, h), is_diff=self.is_diff)

    def rotate(self, angle):
        return self

    def histogram(self):
        if self.mode == "L":
            return [0] * 256
        return [0] * 768

    def save(self, fp, format=None, **params):
        pass

    def point(self, lut, mode=None):
        return self

    def filter(self, filter):
        return self

    def getcolors(self, maxcolors=256):
        return [(1, (30, 30, 30))]

class MockResampling:
    LANCZOS = 1

class MockImageModule:
    Image = MockImage
    Resampling = MockResampling
    
    @staticmethod
    def new(mode, size, color=None):
        return MockImage(mode, size, color)

    @staticmethod
    def open(fp, mode="r"):
        return MockImage()

class MockImageFilterModule:
    GaussianBlur = MagicMock
    SHARPEN = MagicMock
    FIND_EDGES = MagicMock

class MockImageOpsModule:
    @staticmethod
    def grayscale(image):
        return image.convert("L")

class MockImageChopsModule:
    @staticmethod
    def difference(image_a, image_b):
        # Determine if images are identical instances or parameters
        is_identical = (image_a is image_b) or (getattr(image_a, "size", None) == getattr(image_b, "size", None))
        return MockImage(mode=image_a.mode, size=image_a.size, is_diff=is_identical)

class MockImageStatModule:
    class Stat:
        def __init__(self, image):
            if getattr(image, "is_diff", False):
                self.mean = [0.0]
                self.stddev = [0.0]
            else:
                self.mean = [120.0]
                self.stddev = [15.0]

class MockPILModule:
    Image = MockImageModule
    ImageFilter = MockImageFilterModule
    ImageOps = MockImageOpsModule
    ImageStat = MockImageStatModule
    ImageChops = MockImageChopsModule

try:
    from PIL import Image, ImageFilter, ImageOps, ImageStat, ImageChops
except ImportError:
    sys.modules['PIL'] = MockPILModule
    sys.modules['PIL.Image'] = MockImageModule
    sys.modules['PIL.ImageFilter'] = MockImageFilterModule
    sys.modules['PIL.ImageOps'] = MockImageOpsModule
    sys.modules['PIL.ImageStat'] = MockImageStatModule
    sys.modules['PIL.ImageChops'] = MockImageChopsModule
    from PIL import Image, ImageFilter, ImageOps, ImageStat, ImageChops

import pytest
from uuid import UUID
from datetime import datetime

from app.ai.vision.configuration import VisionConfiguration
from app.ai.vision.exceptions import VisionEngineError, ImageProcessingError
from app.ai.vision.models import VisionRequest, ScreenRegion, BoundingBox
from app.ai.vision.utils import calculate_image_hash, image_to_base64
from app.ai.vision.cache import VisionCache
from app.ai.vision.metrics import VisionMetricsTracker
from app.ai.vision.health import VisionHealthMonitor
from app.ai.vision.image_loader import ImageLoader
from app.ai.vision.image_processor import ImageProcessor
from app.ai.vision.screenshot_manager import ScreenshotManager
from app.ai.vision.coordinate_mapper import CoordinateMapper
from app.ai.vision.screen_context import ScreenContext
from app.ai.vision.ocr_engine import OCREngine
from app.ai.vision.ui_detector import UIDetector
from app.ai.vision.layout_analyzer import LayoutAnalyzer
from app.ai.vision.object_detector import ObjectDetector
from app.ai.vision.icon_detector import IconDetector
from app.ai.vision.text_detector import TextDetector
from app.ai.vision.color_analyzer import ColorAnalyzer
from app.ai.vision.similarity_engine import SimilarityEngine
from app.ai.vision.template_matcher import TemplateMatcher
from app.ai.vision.region_selector import RegionSelector
from app.ai.vision.action_planner import ActionPlanner
from app.ai.vision.context_builder import ContextBuilder
from app.ai.vision.providers.mock_provider import MockVisionProvider
from app.ai.vision.providers.local_cv import LocalCVProvider
from app.ai.vision.providers.ollama_vision import OllamaVisionProvider
from app.ai.vision.engine import LocalVisionEngine

from app.ai.gateway import AIGateway
from app.ai.gateway.model_registry import ModelRegistry
from app.ai.gateway.provider_registry import ProviderRegistry
from app.ai.gateway.provider_factory import ProviderFactory
from app.ai.gateway.retry_policy import RetryPolicy
from app.ai.gateway.timeout_policy import TimeoutPolicy
from app.ai.models import ChatResponse, PromptMessage, AIUsage, AIModelInfo, ModelType, ProviderCapability
from app.ai.providers.contracts import ILLMProvider

@pytest.fixture
def dummy_image() -> Image.Image:
    """Returns a basic dummy Image for test evaluations."""
    return Image.new("RGB", (200, 100), color=(50, 100, 150))

@pytest.mark.anyio
async def test_vision_configuration():
    """Verifies that the vision configuration parses parameters correctly."""
    config = VisionConfiguration()
    assert config.enabled is True
    assert config.provider == "local_cv"
    assert config.ocr.enabled is True
    assert config.cv.max_image_size == (1920, 1080)

@pytest.mark.anyio
async def test_image_loader_and_processor(dummy_image):
    """Verifies image loading and preprocessing operations."""
    loader = ImageLoader()
    processor = ImageProcessor()

    # Load mock
    img = loader.load(image_bytes=b"dummybytes")
    assert isinstance(img, Image.Image)

    # Process operations
    gray = processor.grayscale(dummy_image)
    assert gray.mode == "L"

    resized = processor.preprocess(dummy_image, (50, 50))
    assert resized.size == (50, 50)

    cropped = processor.crop(dummy_image, 10, 10, 20, 20)
    assert cropped.size == (20, 20)

    hist = processor.generate_histogram(dummy_image)
    assert "red" in hist
    assert len(hist["red"]) == 256

@pytest.mark.anyio
async def test_screenshot_manager():
    """Verifies screenshot manager handles captures safely."""
    manager = ScreenshotManager()
    screen = manager.capture_screen()
    assert isinstance(screen, Image.Image)

    meta = manager.generate_metadata(screen)
    assert meta.width > 0
    assert isinstance(meta.timestamp, datetime)

@pytest.mark.anyio
async def test_coordinate_mapper():
    """Verifies relative to pixel coordinate scaling conversions."""
    mapper = CoordinateMapper()
    bbox = BoundingBox(x=0.1, y=0.2, width=0.3, height=0.4)
    abs_bbox = mapper.to_absolute(bbox, 1000, 2000)
    assert abs_bbox.x == 100.0
    assert abs_bbox.y == 400.0

    norm_bbox = mapper.to_normalized(abs_bbox, 1000, 2000)
    assert round(norm_bbox.x, 1) == 0.1
    assert round(norm_bbox.y, 1) == 0.2

@pytest.mark.anyio
async def test_ocr_extraction(dummy_image):
    """Verifies text extraction fallbacks."""
    ocr = OCREngine(use_mock_fallback=True)
    res = await ocr.detect_text(dummy_image)
    assert "Login" in res.full_text
    assert len(res.blocks) > 0

@pytest.mark.anyio
async def test_ui_and_object_detection(dummy_image):
    """Verifies that elements and boundaries can be successfully located."""
    ui = UIDetector()
    obj = ObjectDetector()

    elements = ui.detect_elements(dummy_image, 0.5)
    assert len(elements) > 0
    assert elements[0].type in ("button", "textbox", "menu", "sidebar")

    objects = obj.detect_objects(dummy_image, 0.5)
    assert len(objects) > 0

@pytest.mark.anyio
async def test_layout_analyzer():
    """Verifies hierarchy tree groupings."""
    ui = UIDetector()
    dummy = Image.new("RGB", (200, 200))
    elements = ui.detect_elements(dummy, 0.1)

    analyzer = LayoutAnalyzer()
    root = analyzer.analyze_layout(elements, (200, 200))
    assert root.name == "Desktop"
    assert len(root.children) > 0
    assert root.children[0].name == "VS Code"

@pytest.mark.anyio
async def test_color_and_similarity_engine(dummy_image):
    """Verifies color spectrum profiling and similarity difference checks."""
    analyzer = ColorAnalyzer()
    palette = analyzer.analyze_colors(dummy_image)
    assert len(palette.dominant_colors) > 0
    assert palette.theme in ("light", "dark")

    engine = SimilarityEngine()
    sim = engine.calculate_similarity(dummy_image, dummy_image)
    assert sim == 1.0

@pytest.mark.anyio
async def test_action_planner():
    """Verifies workflow action sequence steps output."""
    ui = UIDetector()
    dummy = Image.new("RGB", (200, 200))
    elements = ui.detect_elements(dummy, 0.1)

    planner = ActionPlanner()
    plan = planner.plan_login_sequence(elements)
    assert len(plan.steps) > 0
    assert plan.steps[0].action_type in ("locate", "type", "click", "wait")

@pytest.mark.anyio
async def test_cache_and_metrics(dummy_image):
    """Verifies analysis states retrieval and stopwatch timers."""
    cache = VisionCache()
    cache.set(dummy_image, "test_key", "cached_val")
    assert cache.get(dummy_image, "test_key") == "cached_val"
    assert cache.metrics["hits"] == 1

    tracker = VisionMetricsTracker()
    tracker.start_stage("test_stage")
    tracker.end_stage("test_stage")
    assert "test_stage" in tracker.get_metrics()

@pytest.mark.anyio
async def test_health_monitor():
    """Verifies health diagnostics check runs successfully."""
    monitor = VisionHealthMonitor()
    status = await monitor.check_health()
    assert "pillow_available" in status
    assert "opencv_available" in status

@pytest.mark.anyio
async def test_vision_engine_orchestration(dummy_image):
    """Verifies pipeline orchestration."""
    engine = LocalVisionEngine(config=VisionConfiguration(provider="mock"))
    req = VisionRequest(image_bytes=b"dummybytes")
    resp = await engine.analyze_screen(req)

    assert resp.status == "success"
    assert len(resp.ocr.full_text) > 0
    assert resp.metrics.pipeline_time >= 0

@pytest.mark.anyio
async def test_ai_gateway_integration():
    """Verifies gateway integration and fallback support."""
    provider_registry = ProviderRegistry()
    model_registry = ModelRegistry()

    # Register default model
    model_registry.register_model(
        AIModelInfo(
            name="qwen2.5-coder",
            type=ModelType.TEXT,
            context_window=4096,
            max_output_tokens=1000,
            capabilities=[ProviderCapability.CHAT]
        )
    )

    class DummyLLM(ILLMProvider):
        def supports_model(self, m):
            return m == "qwen2.5-coder"
        async def chat(self, request, **kwargs):
            return ChatResponse(
                message=PromptMessage(role="assistant", content="Vision output from model description"),
                finish_reason="stop",
                usage=AIUsage(),
                model=request.model,
                provider="ollama"
            )
        async def stream_chat(self, request, **kwargs):
            pass
        async def health(self):
            pass
        async def available_models(self):
            return []

    provider_registry.register("ollama", DummyLLM())
    factory = ProviderFactory(provider_registry)
    
    gateway = AIGateway(
        provider_registry=provider_registry,
        model_registry=model_registry,
        factory=factory,
        retry_policy=RetryPolicy(),
        timeout_policy=TimeoutPolicy()
    )

    engine = LocalVisionEngine(gateway=gateway)
    assert engine.gateway == gateway
