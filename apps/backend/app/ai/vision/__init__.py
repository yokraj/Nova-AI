from __future__ import annotations

import sys
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Global PIL Mocking to prevent imports failures when Pillow is not installed
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
    import PIL
except ImportError:
    sys.modules['PIL'] = MockPILModule
    sys.modules['PIL.Image'] = MockImageModule
    sys.modules['PIL.ImageFilter'] = MockImageFilterModule
    sys.modules['PIL.ImageOps'] = MockImageOpsModule
    sys.modules['PIL.ImageStat'] = MockImageStatModule
    sys.modules['PIL.ImageChops'] = MockImageChopsModule


__all__ = [
    # Core engine
    "LocalVisionEngine",
    # Configuration
    "VisionConfiguration",
    "OCRConfiguration",
    "ScreenshotConfiguration",
    "CVConfiguration",
    # Exceptions
    "VisionEngineError",
    "ImageProcessingError",
    "ScreenshotCaptureError",
    "OCRError",
    "UIElementDetectionError",
    "ActionPlanningError",
    # Domain models
    "VisionRequest",
    "VisionResponse",
    "ScreenRegion",
    "UIElement",
    "OCRBlock",
    "OCRResult",
    "LayoutNode",
    "BoundingBox",
    "ScreenAnalysis",
    "ColorPalette",
    "DetectedObject",
    "ScreenshotMetadata",
    "ActionStep",
    "ActionPlan",
    "VisionMetrics",
    # Interfaces
    "IVisionProvider",
    "IOCRProvider",
    "IScreenshotProvider",
    "IUIElementDetector",
    "IObjectDetector",
    "IImageProcessor",
    "IIconDetector",
    "ILayoutAnalyzer",
    "ISimilarityEngine",
    # Concrete sub-components
    "ImageLoader",
    "ImageProcessor",
    "ScreenshotManager",
    "CoordinateMapper",
    "ScreenContext",
    "UIDetector",
    "LayoutAnalyzer",
    "ObjectDetector",
    "IconDetector",
    "TextDetector",
    "OCREngine",
    "ColorAnalyzer",
    "SimilarityEngine",
    "TemplateMatcher",
    "RegionSelector",
    "ActionPlanner",
    "ContextBuilder",
    "VisionMemory",
    # Concrete providers
    "LocalCVProvider",
    "OllamaVisionProvider",
    "MockVisionProvider",
    # Observability & helpers
    "VisionCache",
    "VisionMetricsTracker",
    "VisionHealthMonitor",
]

_LAZY: dict[str, tuple[str, str]] = {
    # Core engine
    "LocalVisionEngine":         (".engine",                "LocalVisionEngine"),
    # Configuration
    "VisionConfiguration":       (".configuration",         "VisionConfiguration"),
    "OCRConfiguration":          (".configuration",         "OCRConfiguration"),
    "ScreenshotConfiguration":   (".configuration",         "ScreenshotConfiguration"),
    "CVConfiguration":           (".configuration",         "CVConfiguration"),
    # Exceptions
    "VisionEngineError":         (".exceptions",            "VisionEngineError"),
    "ImageProcessingError":      (".exceptions",            "ImageProcessingError"),
    "ScreenshotCaptureError":    (".exceptions",            "ScreenshotCaptureError"),
    "OCRError":                  (".exceptions",            "OCRError"),
    "UIElementDetectionError":   (".exceptions",            "UIElementDetectionError"),
    "ActionPlanningError":       (".exceptions",            "ActionPlanningError"),
    # Domain models
    "VisionRequest":             (".models",                "VisionRequest"),
    "VisionResponse":            (".models",                "VisionResponse"),
    "ScreenRegion":              (".models",                "ScreenRegion"),
    "UIElement":                 (".models",                "UIElement"),
    "OCRBlock":                  (".models",                "OCRBlock"),
    "OCRResult":                 (".models",                "OCRResult"),
    "LayoutNode":                (".models",                "LayoutNode"),
    "BoundingBox":               (".models",                "BoundingBox"),
    "ScreenAnalysis":            (".models",                "ScreenAnalysis"),
    "ColorPalette":              (".models",                "ColorPalette"),
    "DetectedObject":            (".models",                "DetectedObject"),
    "ScreenshotMetadata":        (".models",                "ScreenshotMetadata"),
    "ActionStep":                (".models",                "ActionStep"),
    "ActionPlan":                (".models",                "ActionPlan"),
    "VisionMetrics":             (".models",                "VisionMetrics"),
    # Interfaces
    "IVisionProvider":           (".interfaces",            "IVisionProvider"),
    "IOCRProvider":              (".interfaces",            "IOCRProvider"),
    "IScreenshotProvider":       (".interfaces",            "IScreenshotProvider"),
    "IUIElementDetector":        (".interfaces",            "IUIElementDetector"),
    "IObjectDetector":           (".interfaces",            "IObjectDetector"),
    "IImageProcessor":           (".interfaces",            "IImageProcessor"),
    "IIconDetector":             (".interfaces",            "IIconDetector"),
    "ILayoutAnalyzer":           (".interfaces",            "ILayoutAnalyzer"),
    "ISimilarityEngine":         (".interfaces",            "ISimilarityEngine"),
    # Concrete sub-components
    "ImageLoader":               (".image_loader",          "ImageLoader"),
    "ImageProcessor":            (".image_processor",       "ImageProcessor"),
    "ScreenshotManager":         (".screenshot_manager",    "ScreenshotManager"),
    "CoordinateMapper":          (".coordinate_mapper",     "CoordinateMapper"),
    "ScreenContext":             (".screen_context",        "ScreenContext"),
    "UIDetector":                (".ui_detector",           "UIDetector"),
    "LayoutAnalyzer":            (".layout_analyzer",       "LayoutAnalyzer"),
    "ObjectDetector":            (".object_detector",       "ObjectDetector"),
    "IconDetector":              (".icon_detector",         "IconDetector"),
    "TextDetector":              (".text_detector",         "TextDetector"),
    "OCREngine":                 (".ocr_engine",            "OCREngine"),
    "ColorAnalyzer":             (".color_analyzer",        "ColorAnalyzer"),
    "SimilarityEngine":          (".similarity_engine",     "SimilarityEngine"),
    "TemplateMatcher":           (".template_matcher",      "TemplateMatcher"),
    "RegionSelector":            (".region_selector",       "RegionSelector"),
    "ActionPlanner":             (".action_planner",        "ActionPlanner"),
    "ContextBuilder":            (".context_builder",       "ContextBuilder"),
    "VisionMemory":              (".memory",                "VisionMemory"),
    # Concrete providers
    "LocalCVProvider":           (".providers.local_cv",     "LocalCVProvider"),
    "OllamaVisionProvider":      (".providers.ollama_vision", "OllamaVisionProvider"),
    "MockVisionProvider":        (".providers.mock_provider", "MockVisionProvider"),
    # Observability & helpers
    "VisionCache":               (".cache",                 "VisionCache"),
    "VisionMetricsTracker":      (".metrics",               "VisionMetricsTracker"),
    "VisionHealthMonitor":       (".health",                "VisionHealthMonitor"),
}

def __getattr__(name: str):  # noqa: ANN001, ANN201
    """Resolve vision package exports on first access (PEP 562)."""
    if name in _LAZY:
        module_path, attr = _LAZY[name]
        import importlib
        module = importlib.import_module(module_path, package=__name__)
        obj = getattr(module, attr)
        globals()[name] = obj
        return obj
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
