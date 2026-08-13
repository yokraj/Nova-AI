"""HuggingFace Transformers & PyTorch local model provider implementation.
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


class TransformersProvider(IModelProvider):
    """HuggingFace Transformers PyTorch provider."""

    @property
    def provider_name(self) -> str:
        return "transformers"

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        model_id = request.model_id or "Qwen/Qwen2.5-7B-Instruct"
        text = f"[Transformers PyTorch - {model_id}] Output for: {request.prompt[:100]}"
        return GenerationResponse(text=text, model_id=model_id, token_usage=TokenUsage(total_tokens=40))

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        return EmbeddingResponse(embeddings=[[0.1] * 768 for _ in request.text_list], dimensions=768)

    async def process_audio(self, request: AudioRequest) -> AudioResponse:
        return AudioResponse(transcript_or_audio_path="Transformers Audio Output")

    async def process_vision(self, request: VisionRequest) -> VisionResponse:
        return VisionResponse(description="Transformers Vision Output")
