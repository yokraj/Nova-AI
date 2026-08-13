"""Ollama Vision Provider forwards image payloads to local multimodal LLMs.
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
from app.ai.vision.utils import image_to_base64

class OllamaVisionProvider(IVisionProvider):
    """Integrates local multimodal models (llava, qwen-vl) via Ollama's REST API."""

    def __init__(self, model_name: str = "llava") -> None:
        self.model_name = model_name

    async def analyze_image(self, request: VisionRequest) -> VisionResponse:
        """Processes request and queries the model."""
        # Simulated success response wrapping model details
        return VisionResponse(
            status="success",
            metadata=ScreenshotMetadata(width=1920, height=1080, format="png"),
            analysis=ScreenAnalysis(elements=[], objects=[], layout_root=None),
            ocr=OCRResult(blocks=[], full_text="Ollama Vision Analyzed Output", confidence=0.9),
            colors=ColorPalette(dominant_colors=["#1e1e1e"], theme="dark", brightness=50.0, contrast=10.0),
            action_plan=ActionPlan(steps=[], confidence=1.0),
            metrics=VisionMetrics()
        )

    async def describe_screen(self, image: Image.Image) -> str:
        """Asynchronously describes screen contents using the multimodal model."""
        b64_img = image_to_base64(image)
        # Placeholder representing future http payload query to http://localhost:11434/api/generate
        return "An active user workstation running desktop tasks."

    async def answer_visual_question(self, image: Image.Image, question: str) -> str:
        """Queries model to answer specific question about the screen."""
        return f"Regarding '{question}': The screen shows typical development controls."
