"""LLM Runtime executing text generation, reasoning, coding, and tool calling via OllamaProvider.
"""

from typing import Any, AsyncGenerator, Dict, Optional
from app.ai.models.models import GenerationRequest
from app.ai.models.providers.ollama_provider import OllamaProvider
from app.ai.runtime.interfaces import ILLMRuntime
from app.ai.runtime.models import DeviceType, RuntimeRequest, RuntimeResponse


class LLMRuntime(ILLMRuntime):
    """LLM execution runtime connecting to local Ollama provider."""

    def __init__(self, ollama_provider: Optional[OllamaProvider] = None) -> None:
        self.provider = ollama_provider or OllamaProvider()

    async def generate(self, request: RuntimeRequest) -> RuntimeResponse:
        """Executes text/code/reasoning generation request via OllamaProvider."""
        model_id = request.model_id or "qwen3:8b"
        gen_req = GenerationRequest(
            prompt=request.prompt,
            model_id=model_id,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        res = await self.provider.generate(gen_req)

        return RuntimeResponse(
            model_id=res.model_id,
            text_or_data=res.text,
            finish_reason="stop",
            token_usage={
                "prompt_tokens": res.token_usage.prompt_tokens,
                "completion_tokens": res.token_usage.completion_tokens,
                "total_tokens": res.token_usage.total_tokens,
            },
            latency_ms=120.0,
            device_used=DeviceType.CUDA,
        )

    async def generate_stream(self, request: RuntimeRequest) -> AsyncGenerator[str, None]:
        """Streams text chunks from OllamaProvider."""
        model_id = request.model_id or "qwen3:8b"
        gen_req = GenerationRequest(
            prompt=request.prompt,
            model_id=model_id,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        async for chunk in self.provider.generate_stream(gen_req):
            yield chunk
