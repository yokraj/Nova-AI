"""OpenAI API provider implementation.
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


class OpenAIProvider(IModelProvider):
    """OpenAI remote API provider."""

    @property
    def provider_name(self) -> str:
        return "openai"

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        model_id = request.model_id or "gpt-4o"
        text = f"[OpenAI API - {model_id}] Output for prompt: {request.prompt[:100]}"
        return GenerationResponse(text=text, model_id=model_id, token_usage=TokenUsage(total_tokens=45))

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        return EmbeddingResponse(embeddings=[[0.01] * 1536 for _ in request.text_list], dimensions=1536)

    async def process_audio(self, request: AudioRequest) -> AudioResponse:
        return AudioResponse(transcript_or_audio_path="OpenAI Whisper API Output")

    async def process_vision(self, request: VisionRequest) -> VisionResponse:
        return VisionResponse(description="OpenAI Vision API Output")
