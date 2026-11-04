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
    """OpenAI remote API provider (Disabled under Zero-Cost Policy)."""

    @property
    def provider_name(self) -> str:
        return "openai"

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        raise PermissionError(
            "Commercial provider 'openai' is disabled under Nova AI Zero-Cost Policy. "
            "Please use local Ollama inference ('ollama') instead."
        )

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raise PermissionError(
            "Commercial provider 'openai' embeddings are disabled under Nova AI Zero-Cost Policy. "
            "Please use local embeddings ('nomic-embed-text' via Ollama) instead."
        )

    async def process_audio(self, request: AudioRequest) -> AudioResponse:
        raise PermissionError(
            "Commercial provider 'openai' audio processing is disabled under Nova AI Zero-Cost Policy. "
            "Please use local faster-whisper instead."
        )

    async def process_vision(self, request: VisionRequest) -> VisionResponse:
        raise PermissionError(
            "Commercial provider 'openai' vision is disabled under Nova AI Zero-Cost Policy. "
            "Please use local vision models ('qwen2.5-vl' via Ollama) instead."
        )
