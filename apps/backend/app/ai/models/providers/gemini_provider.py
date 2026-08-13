"""Google Gemini API provider implementation.
"""

from app.ai.models.interfaces import IModelProvider
from app.ai.models.models import (
    AudioRequest,
    AudioResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    GenerationRequest,
    GenerationResponse,
    TokenUsage,
    VisionRequest,
    VisionResponse,
)


class GeminiProvider(IModelProvider):
    """Google Gemini remote API provider."""

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        model_id = request.model_id or "gemini-1.5-pro"
        text = f"[Gemini API - {model_id}] Output for prompt: {request.prompt[:100]}"
        return GenerationResponse(text=text, model_id=model_id, token_usage=TokenUsage(total_tokens=40))

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        return EmbeddingResponse(embeddings=[[0.02] * 768 for _ in request.text_list], dimensions=768)

    async def process_audio(self, request: AudioRequest) -> AudioResponse:
        return AudioResponse(transcript_or_audio_path="Gemini Audio API Output")

    async def process_vision(self, request: VisionRequest) -> VisionResponse:
        return VisionResponse(description="Gemini Vision API Output")
