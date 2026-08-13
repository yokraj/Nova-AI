"""Interfaces outlining contracts for Vision Engine modules and providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from PIL import Image

from app.ai.vision.models import (
    VisionRequest,
    VisionResponse,
    UIElement,
    DetectedObject,
    OCRResult,
    LayoutNode,
    ColorPalette,
    ScreenRegion,
)

class IVisionProvider(ABC):
    """Abstract interface for high-level screen describing and reasoning providers."""

    @abstractmethod
    async def analyze_image(self, request: VisionRequest) -> VisionResponse:
        """Processes an image and returns high-level visual descriptions and structures."""
        pass

    @abstractmethod
    async def describe_screen(self, image: Image.Image) -> str:
        """Generates a text description of the screen context."""
        pass

class IOCRProvider(ABC):
    """Abstract interface for local optical character recognition."""

    @abstractmethod
    async def detect_text(self, image: Image.Image) -> OCRResult:
        """Identifies text blocks and extracts character contents."""
        pass

class IScreenshotProvider(ABC):
    """Abstract interface for screen capturing drivers."""

    @abstractmethod
    def capture_screen(self) -> Image.Image:
        """Captures the entire desktop viewport."""
        pass

    @abstractmethod
    def capture_window(self, window_title: str) -> Image.Image:
        """Captures bounds of the target window application."""
        pass

    @abstractmethod
    def capture_region(self, region: ScreenRegion) -> Image.Image:
        """Captures a subset rectangular region of the screen."""
        pass

class IUIElementDetector(ABC):
    """Abstract interface for identifying interactive user interface controls."""

    @abstractmethod
    def detect_elements(self, image: Image.Image, confidence_threshold: float) -> List[UIElement]:
        """Scans the image and extracts structural controls (buttons, forms, dropdowns)."""
        pass

class IObjectDetector(ABC):
    """Abstract interface for generic object detection."""

    @abstractmethod
    def detect_objects(self, image: Image.Image, confidence_threshold: float) -> List[DetectedObject]:
        """Scans the image and flags object boundaries."""
        pass

class IImageProcessor(ABC):
    """Abstract interface for applying pre-processing filters and resizing."""

    @abstractmethod
    def preprocess(self, image: Image.Image, target_size: Optional[tuple[int, int]] = None) -> Image.Image:
        """Resizes, sharpens, or grayscales target image to normalize inputs."""
        pass

class IIconDetector(ABC):
    """Abstract interface for identifying known system and application icons."""

    @abstractmethod
    def detect_icons(self, image: Image.Image, templates: Dict[str, Image.Image]) -> List[UIElement]:
        """Finds matching app icons using template visual files."""
        pass

class ILayoutAnalyzer(ABC):
    """Abstract interface for building containment hierarchies of UI layout blocks."""

    @abstractmethod
    def analyze_layout(self, elements: List[UIElement], image_size: tuple[int, int]) -> LayoutNode:
        """Groups flat elements lists into nested spatial block hierarchies."""
        pass

class ISimilarityEngine(ABC):
    """Abstract interface for matching image similarity scores."""

    @abstractmethod
    def calculate_similarity(self, image_a: Image.Image, image_b: Image.Image) -> float:
        """Compares visual structures and returns match score coefficient (0 to 1)."""
        pass
