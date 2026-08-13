"""Anthropic Claude API provider implementation.
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


class AnthropicProvider(IModelProvider):
    """Anthropic Claude remote API provider."""

    @property
    def provider_name(self) -> str:
        return "anthropic"

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        model_id = request.model_id or "claude-3-5-sonnet"
        text = f"[Anthropic API - {model_id}] Output for prompt: {request.prompt[:100]}"
        return GenerationResponse(text=text, model_id=model_id, token_usage=TokenUsage(total_tokens=50))

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        return EmbeddingResponse(embeddings=[[0.03] * 1024 for _ in request.text_list], dimensions=1024)

    async def process_audio(self, request: AudioRequest) -> AudioResponse:
        return AudioResponse(transcript_or_audio_path="Anthropic Audio N/A")

    async def process_vision(self, request: VisionRequest) -> VisionResponse:
        return VisionResponse(description="Anthropic Vision API Output")
