"""Mock Model Provider for offline unit tests and CI integration.
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


class MockModelProvider(IModelProvider):
    """Mock Model Provider returning deterministic test responses."""

    @property
    def provider_name(self) -> str:
        return "mock_provider"

    async def generate(self, request: Optional[GenerationRequest] = None) -> GenerationResponse:
        model_id = request.model_id if request and hasattr(request, "model_id") and request.model_id else "mock-model-v1"
        prompt = request.prompt if request and hasattr(request, "prompt") else "test prompt"
        return GenerationResponse(
            text=f"[Mock Response] Generated output for: {prompt}",
            finish_reason="stop",
            token_usage=TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
            model_id=model_id,
        )

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        texts = request.text_list if request and hasattr(request, "text_list") else ["test"]
        return EmbeddingResponse(
            embeddings=[[0.1 * i for i in range(768)] for _ in texts],
            dimensions=768,
            token_count=15,
        )

    async def process_audio(self, request: AudioRequest) -> AudioResponse:
        return AudioResponse(transcript_or_audio_path="Mock Audio Result", language="en")

    async def process_vision(self, request: Optional[VisionRequest] = None) -> VisionResponse:
        return VisionResponse(description="Mock Vision Analysis", detected_objects=["mock_object"])

