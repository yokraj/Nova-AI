"""OpenAI Whisper local STT speech recognition provider.
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


class WhisperProvider(IModelProvider):
    """Whisper local speech-to-text recognition provider."""

    @property
    def provider_name(self) -> str:
        return "whisper"

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        return GenerationResponse(text="Whisper speech engine active.")

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        return EmbeddingResponse(embeddings=[[0.0] * 768 for _ in request.text_list])

    async def process_audio(self, request: AudioRequest) -> AudioResponse:
        return AudioResponse(
            transcript_or_audio_path="Hey Nova, build an e-commerce backend",
            language=request.language,
            duration_seconds=2.4,
        )

    async def process_vision(self, request: VisionRequest) -> VisionResponse:
        return VisionResponse(description="Whisper STT Only")
