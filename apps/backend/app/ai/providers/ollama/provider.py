"""Concrete Ollama provider adapter implementing LLM and Embedding contracts.
"""

from typing import Any, AsyncGenerator, List
from app.ai.models import (
    AIModelInfo,
    AIUsage,
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    FinishReason,
    ModelType,
    PromptMessage,
    ProviderCapability,
    ProviderHealth,
    StreamingChunk,
    TokenUsage,
)
from app.ai.providers.contracts import IEmbeddingProvider, ILLMProvider
from app.ai.providers.ollama.client import OllamaClient
from app.ai.providers.ollama.config import OllamaConfig
from app.ai.providers.ollama.health import OllamaHealthCheck


class OllamaProvider(ILLMProvider, IEmbeddingProvider):
    """Concrete Ollama provider adapter implementing LLM and Embedding contracts."""

    def __init__(self, config: OllamaConfig, client: OllamaClient) -> None:
        """Initializes OllamaProvider.

        Args:
            config: OllamaConfig options.
            client: OllamaClient communications instance.
        """
        self.config = config
        self.client = client
        self.health_check = OllamaHealthCheck(client)

    def supports_model(self, model: str) -> bool:
        """Checks if provider supports model (defaults to true for mock setups)."""
        return True

    async def chat(self, request: ChatRequest, **kwargs: Any) -> ChatResponse:
        """Sends chat completions query to Ollama."""
        messages_payload = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        payload = {
            "model": request.model,
            "messages": messages_payload,
            "stream": False,
            "options": {"temperature": request.temperature},
        }
        if request.max_tokens:
            payload["options"]["num_predict"] = request.max_tokens

        resp = await self.client.post("/api/chat", payload)
        message_data = resp.get("message", {})

        prompt_tokens = resp.get("prompt_eval_count", 0)
        completion_tokens = resp.get("eval_count", 0)

        usage = AIUsage(
            token_usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            )
        )

        return ChatResponse(
            message=PromptMessage(
                role=message_data.get("role", "assistant"),
                content=message_data.get("content", ""),
            ),
            finish_reason=FinishReason.STOP,
            usage=usage,
            model=request.model,
            provider="ollama",
        )

    async def stream_chat(
        self, request: ChatRequest, **kwargs: Any
    ) -> AsyncGenerator[StreamingChunk, None]:
        """Streams chat completions chunks from Ollama."""
        messages_payload = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        payload = {
            "model": request.model,
            "messages": messages_payload,
            "stream": True,
            "options": {"temperature": request.temperature},
        }
        if request.max_tokens:
            payload["options"]["num_predict"] = request.max_tokens

        async for chunk in self.client.post_stream("/api/chat", payload):
            message_data = chunk.get("message", {})
            content = message_data.get("content", "")

            usage = None
            finish_reason = None
            if chunk.get("done", False):
                finish_reason = FinishReason.STOP
                prompt_tokens = chunk.get("prompt_eval_count", 0)
                completion_tokens = chunk.get("eval_count", 0)
                usage = AIUsage(
                    token_usage=TokenUsage(
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=prompt_tokens + completion_tokens,
                    )
                )

            yield StreamingChunk(content=content, finish_reason=finish_reason, usage=usage)

    async def embed_text(self, request: EmbeddingRequest, **kwargs: Any) -> EmbeddingResponse:
        """Generates embedding vectors for a batch of text inputs."""
        embeddings = []
        for prompt_text in request.input:
            payload = {
                "model": request.model,
                "prompt": prompt_text,
            }
            resp = await self.client.post("/api/embeddings", payload)
            embeddings.append(resp.get("embedding", []))

        return EmbeddingResponse(
            embeddings=embeddings,
            usage=AIUsage(),
            model=request.model,
        )

    async def embed_batch(self, request: EmbeddingRequest, **kwargs: Any) -> EmbeddingResponse:
        """Generates embedding vectors for batch queries."""
        return await self.embed_text(request, **kwargs)

    async def health(self) -> ProviderHealth:
        """Performs diagnostics health validation."""
        return await self.health_check.check_health(self.config.default_model)

    async def available_models(self) -> List[AIModelInfo]:
        """Retrieves models active on Ollama server."""
        try:
            resp = await self.client.get("/api/tags")
            models = resp.get("models", [])
            return [
                AIModelInfo(
                    name=m.get("name", ""),
                    type=ModelType.TEXT,
                    context_window=2048,
                    max_output_tokens=500,
                    capabilities=[ProviderCapability.CHAT, ProviderCapability.EMBEDDINGS],
                )
                for m in models
            ]
        except Exception:
            return []
