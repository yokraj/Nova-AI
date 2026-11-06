"""Provider Router Module for Nova AI Enterprise Core Intelligence.

Routes HTTP inference calls to target provider backends (Ollama, OpenAI, Anthropic)
with real multi-turn chat support, Qwen3 thinking token capture, bounded timeouts,
and zero mock fallbacks.
"""

import json
import time
from typing import Any, Dict, List, Optional
import httpx
import structlog

from app.inference.config import InferenceConfig
from app.inference.provider_manager import ProviderManager
from app.core.zero_cost_policy import ZeroCostPolicy, ZeroCostPolicyViolation

logger = structlog.get_logger(__name__)


class ProviderRouter:
    """Enterprise Provider Route Dispatcher with Multi-Turn & Thinking Support."""

    def __init__(
        self,
        config: Optional[InferenceConfig] = None,
        provider_manager: Optional[ProviderManager] = None,
    ) -> None:
        self.config = config or InferenceConfig()
        self.provider_manager = provider_manager or ProviderManager(config=self.config)
        logger.info("provider_router_initialized")

    async def is_ollama_available(self) -> bool:
        """Verifies if local Ollama daemon is reachable and responding."""
        try:
            url = f"{self.config.ollama_base_url.rstrip('/')}/api/tags"
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(url)
                return res.status_code == 200
        except Exception:
            return False

    async def dispatch_request(
        self,
        provider: str,
        model: str,
        prompt: str,
        messages: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Dispatches completion call to target provider backend (Real Local/Cloud execution)."""
        target_provider = (provider or self.config.default_provider).lower()
        target_model = model or self.config.default_model

        # Strictly enforce Zero-Cost Policy: Block commercial providers before any network call
        ZeroCostPolicy.assert_llm_provider_allowed(target_provider)

        logger.info(
            "request_dispatched",
            provider=target_provider,
            model=target_model,
            has_history=bool(messages),
            tools_count=len(tools) if tools else 0,
        )

        if target_provider in ("ollama", "local"):
            # Check availability before long dispatch
            is_online = await self.is_ollama_available()
            if not is_online:
                raise RuntimeError(
                    f"Local AI inference engine (Ollama on {self.config.ollama_base_url}) is offline or unreachable. "
                    f"Please ensure Ollama is running and model '{target_model}' is pulled."
                )

            options: Dict[str, Any] = {}
            if max_tokens:
                options["num_predict"] = max_tokens
            if temperature is not None:
                options["temperature"] = temperature

            # When tools are requested, execute structured function calling via Ollama /api/chat
            if tools:
                endpoint = f"{self.config.ollama_base_url.rstrip('/')}/api/chat"
                chat_messages: List[Dict[str, Any]] = []
                if system_prompt:
                    chat_messages.append({"role": "system", "content": system_prompt})
                if messages:
                    chat_messages.extend(messages)
                # Ensure the current prompt or state is represented
                if not chat_messages:
                    chat_messages.append({"role": "user", "content": prompt})
                elif chat_messages[-1].get("role") not in ("user", "tool", "assistant"):
                    chat_messages.append({"role": "user", "content": prompt})
                elif chat_messages[-1].get("role") == "user" and chat_messages[-1].get("content") != prompt:
                    chat_messages.append({"role": "user", "content": prompt})

                payload: Dict[str, Any] = {
                    "model": target_model,
                    "messages": chat_messages,
                    "tools": tools,
                    "stream": False,
                }
                if options:
                    payload["options"] = options

                try:
                    timeout = httpx.Timeout(connect=15.0, read=120.0, write=15.0, pool=15.0)
                    async with httpx.AsyncClient(timeout=timeout) as client:
                        response = await client.post(endpoint, json=payload)
                        response.raise_for_status()
                        res_data = response.json()

                    msg = res_data.get("message", {})
                    raw_content = msg.get("content", "")
                    thinking = msg.get("thinking", "")
                    raw_tool_calls = msg.get("tool_calls", [])

                    normalized_tool_calls: List[Dict[str, Any]] = []
                    for idx, tc in enumerate(raw_tool_calls):
                        func = tc.get("function", {})
                        fn_name = func.get("name", "")
                        fn_args = func.get("arguments", {})
                        if isinstance(fn_args, str):
                            try:
                                fn_args = json.loads(fn_args)
                            except Exception:
                                fn_args = {"raw": fn_args}
                        elif not isinstance(fn_args, dict):
                            fn_args = {"value": fn_args}

                        tc_id = tc.get("id") or f"call_{fn_name}_{idx}_{int(time.time())}"
                        normalized_tool_calls.append({
                            "id": tc_id,
                            "name": fn_name,
                            "arguments": fn_args,
                        })

                    prompt_tokens = res_data.get("prompt_eval_count", 0) or int(len(prompt.split()) * 1.3)
                    completion_tokens = res_data.get("eval_count", 0) or int(len((raw_content or "").split()) * 1.3)

                    return {
                        "content": raw_content,
                        "thinking": thinking,
                        "tool_calls": normalized_tool_calls,
                        "provider": target_provider,
                        "model": target_model,
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                    }
                except Exception as exc:
                    logger.error("ollama_tool_dispatch_failed", error=str(exc))
                    raise

            # Decide whether to use /api/chat (for multi-turn) or /api/generate
            if messages and len(messages) > 0:
                endpoint = f"{self.config.ollama_base_url.rstrip('/')}/api/chat"
                chat_messages = []
                if system_prompt:
                    chat_messages.append({"role": "system", "content": system_prompt})
                chat_messages.extend(messages)
                # Ensure the current prompt is included as the latest user turn if not already
                if not chat_messages or chat_messages[-1].get("content") != prompt:
                    chat_messages.append({"role": "user", "content": prompt})

                payload = {
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

            full_chunks = []
            prompt_tokens = 0
            completion_tokens = 0
            is_thinking = False

            try:
                timeout = httpx.Timeout(connect=15.0, read=120.0, write=15.0, pool=15.0)
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
                                    thinking_chunk = msg.get("thinking", "")
                                    response_chunk = msg.get("content", "")
                                else:
                                    thinking_chunk = chunk.get("thinking", "")
                                    response_chunk = chunk.get("response", "")

                                if thinking_chunk:
                                    if not is_thinking:
                                        full_chunks.append("<think>")
                                        is_thinking = True
                                    full_chunks.append(thinking_chunk)

                                if response_chunk:
                                    if is_thinking:
                                        full_chunks.append("</think>\n\n")
                                        is_thinking = False
                                    full_chunks.append(response_chunk)

                                if chunk.get("done"):
                                    if is_thinking:
                                        full_chunks.append("</think>\n\n")
                                        is_thinking = False
                                    prompt_tokens = chunk.get("prompt_eval_count", 0)
                                    completion_tokens = chunk.get("eval_count", 0)
                                    break
                            except Exception:
                                continue

                content = "".join(full_chunks).strip()
                if not content:
                    raise RuntimeError(f"Ollama returned an empty generation response for model '{target_model}'.")

                if not prompt_tokens:
                    prompt_tokens = int(len(prompt.split()) * 1.3)
                if not completion_tokens:
                    completion_tokens = int(len(content.split()) * 1.3)

                return {
                    "content": content,
                    "thinking": "",
                    "tool_calls": [],
                    "provider": target_provider,
                    "model": target_model,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                }
            except Exception as exc:
                logger.error("ollama_dispatch_failed", error=str(exc))
                raise

        raise ZeroCostPolicyViolation(
            f"Provider '{target_provider}' is disabled under the Nova AI Zero-Cost Policy. "
            f"Only local providers ('ollama') are authorized to guarantee zero cost and data privacy."
        )
