"""BGE / SentenceTransformers local vector embedding provider.
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


class EmbeddingProvider(IModelProvider):
    """BGE / SentenceTransformers local vector embedding provider."""

    @property
    def provider_name(self) -> str:
        return "bge_embedding"

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        return GenerationResponse(text="BGE Embedding provider active.")

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        dims = 768
        dummy_vectors = [[0.05 * ((i + idx) % 10) for i in range(dims)] for idx in range(len(request.text_list))]
        return EmbeddingResponse(embeddings=dummy_vectors, dimensions=dims, token_count=len(request.text_list) * 15)

    async def process_audio(self, request: AudioRequest) -> AudioResponse:
        return AudioResponse(transcript_or_audio_path="Embedding N/A")

    async def process_vision(self, request: VisionRequest) -> VisionResponse:
        return VisionResponse(description="Embedding N/A")
