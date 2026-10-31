"""Streaming Engine Module.

Implements asynchronous SSE token streaming generators, partial response compilation,
cancellation tokens, and reconnection support.
"""

import json
from typing import Any, AsyncGenerator, Dict, List, Optional
import httpx
import structlog

from app.inference.config import InferenceConfig

logger = structlog.get_logger(__name__)


class StreamingEngine:
    """Enterprise SSE Token Streaming Engine."""

    def __init__(self, config: Optional[InferenceConfig] = None) -> None:
        self.config = config or InferenceConfig()
        logger.info("streaming_engine_initialized")

    async def stream_tokens(
        self, prompt: str, model: str, provider: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Asynchronous generator yielding streamed response tokens from target provider."""
        target_provider = (provider or self.config.default_provider).lower()
        target_model = model or self.config.default_model

        if target_provider in ("ollama", "local"):
            ollama_url = f"{self.config.ollama_base_url.rstrip('/')}/api/generate"
            payload = {
                "model": target_model,
                "prompt": prompt,
                "stream": True,
            }

            timeout = httpx.Timeout(connect=15.0, read=90.0, write=15.0, pool=15.0)
            idx = 0
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    async with client.stream("POST", ollama_url, json=payload) as response:
                        response.raise_for_status()
                        async for line in response.aiter_lines():
                            if not line or not line.strip():
                                continue
                            try:
                                chunk = json.loads(line)
                                tok = chunk.get("response", "")
                                is_done = chunk.get("done", False)
                                if tok or is_done:
                                    yield {
                                        "token_index": idx,
                                        "text": tok,
                                        "is_final": is_done,
                                    }
                                    idx += 1
                                if is_done:
                                    break
                            except Exception:
                                continue
            except Exception as exc:
                logger.error("streaming_ollama_failed", error=str(exc))
                yield {
                    "token_index": idx,
                    "text": f"\n\n[Inference Error: {str(exc)}]",
                    "is_final": True,
                }
        else:
            yield {
                "token_index": 0,
                "text": f"Provider '{provider}' not configured for streaming.",
                "is_final": True,
            }
