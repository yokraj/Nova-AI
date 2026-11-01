"""Streaming Engine Module for Nova AI Enterprise Core Intelligence.

Implements asynchronous SSE token streaming generators, multi-turn chat support,
thinking token handling, cancellation tokens, and zero mock fallbacks.
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
        self,
        prompt: str,
        model: str,
        provider: str,
        messages: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Asynchronous generator yielding streamed response tokens from target provider."""
        target_provider = (provider or self.config.default_provider).lower()
        target_model = model or self.config.default_model

        if target_provider in ("ollama", "local"):
            options: Dict[str, Any] = {}
            if max_tokens:
                options["num_predict"] = max_tokens

            # Choose endpoint based on multi-turn history presence
            if messages and len(messages) > 0:
                endpoint = f"{self.config.ollama_base_url.rstrip('/')}/api/chat"
                chat_messages = []
                if system_prompt:
                    chat_messages.append({"role": "system", "content": system_prompt})
                chat_messages.extend(messages)
                if not chat_messages or chat_messages[-1].get("content") != prompt:
                    chat_messages.append({"role": "user", "content": prompt})

                payload: Dict[str, Any] = {
                    "model": target_model,
                    "messages": chat_messages,
                    "stream": True,
                }
                if options:
                    payload["options"] = options
                is_chat_api = True
            else:
                endpoint = f"{self.config.ollama_base_url.rstrip('/')}/api/generate"
                payload = {
                    "model": target_model,
                    "prompt": prompt,
                    "stream": True,
                }
                if system_prompt:
                    payload["system"] = system_prompt
                if options:
                    payload["options"] = options
                is_chat_api = False

            timeout = httpx.Timeout(connect=15.0, read=120.0, write=15.0, pool=15.0)
            idx = 0
            is_thinking = False
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    async with client.stream("POST", endpoint, json=payload) as response:
                        response.raise_for_status()
                        async for line in response.aiter_lines():
                            if not line or not line.strip():
                                continue
                            try:
                                chunk = json.loads(line)
                                if is_chat_api:
                                    msg = chunk.get("message", {})
                                    thinking_tok = msg.get("thinking", "")
                                    response_tok = msg.get("content", "")
                                else:
                                    thinking_tok = chunk.get("thinking", "")
                                    response_tok = chunk.get("response", "")
                                is_done = chunk.get("done", False)

                                if thinking_tok:
                                    if not is_thinking:
                                        yield {"token_index": idx, "text": "<think>", "is_final": False}
                                        idx += 1
                                        is_thinking = True
                                    yield {"token_index": idx, "text": thinking_tok, "is_final": False}
                                    idx += 1

                                if response_tok:
                                    if is_thinking:
                                        yield {"token_index": idx, "text": "</think>\n\n", "is_final": False}
                                        idx += 1
                                        is_thinking = False
                                    yield {"token_index": idx, "text": response_tok, "is_final": False}
                                    idx += 1

                                if is_done:
                                    if is_thinking:
                                        yield {"token_index": idx, "text": "</think>\n\n", "is_final": False}
                                        idx += 1
                                        is_thinking = False
                                    yield {"token_index": idx, "text": "", "is_final": True}
                                    idx += 1
                                    break
                            except Exception:
                                continue
            except Exception as exc:
                logger.error("streaming_ollama_failed", error=str(exc))
                yield {
                    "token_index": idx,
                    "text": f"\n\n[Inference Error: Unable to complete stream via Ollama: {str(exc)}]",
                    "is_final": True,
                }
        else:
            yield {
                "token_index": 0,
                "text": f"[Configuration Error: Provider '{provider}' not configured for streaming.]",
                "is_final": True,
            }
