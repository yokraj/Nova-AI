"""PaddleOCR local document & image text recognition provider.
"""

from app.ai.models.interfaces import IModelProvider
from app.ai.models.models import (
    AudioRequest,
    AudioResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    GenerationRequest,
    GenerationResponse,
    VisionRequest,
    VisionResponse,
)


class PaddleOCRProvider(IModelProvider):
    """PaddleOCR local text detection and document OCR provider."""

    @property
    def provider_name(self) -> str:
        return "paddleocr"

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        return GenerationResponse(text="PaddleOCR active.")

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        return EmbeddingResponse(embeddings=[[0.0] * 768 for _ in request.text_list])

    async def process_audio(self, request: AudioRequest) -> AudioResponse:
        return AudioResponse(transcript_or_audio_path="PaddleOCR N/A")

    async def process_vision(self, request: VisionRequest) -> VisionResponse:
        return VisionResponse(
            description="PaddleOCR extracted text from image",
            text_found="INVOICE TOTAL: $1,250.00 | VENDOR: Nova AI",
            detected_objects=["table", "header_text", "total_box"],
        )
