"""LLaMA.cpp GGUF local model provider implementation.
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


class LlamaCppProvider(IModelProvider):
    """LLaMA.cpp GGUF local CPU/GPU inference provider."""

    @property
    def provider_name(self) -> str:
        return "llamacpp"

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        model_id = request.model_id or "llama3.2-3b-instruct.Q4_K_M.gguf"
        text = f"[llama.cpp - {model_id}] Generated response for prompt: {request.prompt[:100]}"
        usage = TokenUsage(prompt_tokens=20, completion_tokens=30, total_tokens=50, estimated_cost=0.0)
        return GenerationResponse(text=text, model_id=model_id, token_usage=usage)

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        dims = 1024
        dummy_vector = [0.02 * (i % 10) for i in range(dims)]
        return EmbeddingResponse(embeddings=[dummy_vector for _ in request.text_list], dimensions=dims)

    async def process_audio(self, request: AudioRequest) -> AudioResponse:
        return AudioResponse(transcript_or_audio_path="llama.cpp Audio Output", language="en")

    async def process_vision(self, request: VisionRequest) -> VisionResponse:
        return VisionResponse(description="llama.cpp Vision analysis")
