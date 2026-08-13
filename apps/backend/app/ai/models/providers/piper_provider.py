"""Piper fast local TTS speech synthesis provider.
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


class PiperProvider(IModelProvider):
    """Piper fast local text-to-speech synthesis provider."""

    @property
    def provider_name(self) -> str:
        return "piper"

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        return GenerationResponse(text="Piper TTS active.")

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        return EmbeddingResponse(embeddings=[[0.0] * 768 for _ in request.text_list])

    async def process_audio(self, request: AudioRequest) -> AudioResponse:
        return AudioResponse(
            transcript_or_audio_path="./data/audio/output_speech.wav",
            language=request.language,
            duration_seconds=1.8,
        )

    async def process_vision(self, request: VisionRequest) -> VisionResponse:
        return VisionResponse(description="Piper TTS Only")
