"""Llama.cpp local provider adapter placeholder implementing ILocalModelRuntime.
"""

from typing import Any, AsyncGenerator, List, Dict
from app.ai.runtime.interfaces import ILocalModelRuntime
from app.ai.models import (
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    StreamingChunk,
    PromptMessage,
    AIUsage,
    TokenUsage,
    FinishReason,
    ProviderHealth,
)

class LlamaCppLocalProvider(ILocalModelRuntime):
    """Placeholder for future GGUF and CPU/GPU memory acceleration options."""

    def __init__(self, model_path: str = "") -> None:
        self.model_path = model_path

    async def load_model(self, model_name: str) -> bool:
        return True

    async def unload_model(self, model_name: str) -> bool:
        return True

    async def generate(self, request: ChatRequest, **kwargs: Any) -> ChatResponse:
        return ChatResponse(
            message=PromptMessage(role="assistant", content="Llama.cpp placeholder response"),
            finish_reason=FinishReason.STOP,
            usage=AIUsage(token_usage=TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20)),
            model=request.model,
            provider="llamacpp"
        )

    async def stream_generate(self, request: ChatRequest, **kwargs: Any) -> AsyncGenerator[StreamingChunk, None]:
        yield StreamingChunk(content="Llama.cpp placeholder stream chunk", finish_reason=FinishReason.STOP)

    async def embed(self, request: EmbeddingRequest, **kwargs: Any) -> EmbeddingResponse:
        return EmbeddingResponse(
            embeddings=[[0.1, 0.2, 0.3] for _ in request.input],
            usage=AIUsage(),
            model=request.model
        )

    async def health(self) -> ProviderHealth:
        return ProviderHealth(is_healthy=True, latency_ms=1.0, status_code=200)
