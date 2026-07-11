"""Enterprise AI Gateway core orchestration layer.
"""

import asyncio
from typing import Any, AsyncGenerator, List, Optional
from app.ai.gateway import IAIGateway
from app.ai.gateway.exceptions import (
    CapabilityUnavailableError,
    GatewayTimeoutError,
    ModelUnavailableError,
    ProviderNotFoundError,
    ProviderUnavailableError,
)
from app.ai.gateway.model_registry import ModelRegistry
from app.ai.gateway.provider_factory import ProviderFactory
from app.ai.gateway.provider_registry import ProviderRegistry
from app.ai.gateway.request_context import RequestContext
from app.ai.gateway.retry_policy import RetryPolicy
from app.ai.gateway.timeout_policy import TimeoutPolicy
from app.ai.models import (
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    ProviderCapability,
    StreamingChunk,
)


class AIGateway(IAIGateway):
    """The central enterprise AI Gateway orchestrating routing and execution policies."""

    def __init__(
        self,
        provider_registry: ProviderRegistry,
        model_registry: ModelRegistry,
        factory: ProviderFactory,
        retry_policy: RetryPolicy,
        timeout_policy: TimeoutPolicy,
    ) -> None:
        """Initializes AIGateway.

        Args:
            provider_registry: Active ProviderRegistry.
            model_registry: Active ModelRegistry.
            factory: ProviderFactory helper.
            retry_policy: RetryPolicy configurations.
            timeout_policy: TimeoutPolicy limits configuration.
        """
        self.provider_registry = provider_registry
        self.model_registry = model_registry
        self.factory = factory
        self.retry_policy = retry_policy
        self.timeout_policy = timeout_policy

    def _resolve_provider(self, context: RequestContext, capability: ProviderCapability) -> Any:
        """Resolves provider matching context parameters and validates capabilities.

        Args:
            context: Request context containing model details.
            capability: Target capability enum.

        Returns:
            The matched provider instance.
        """
        model_meta = self.model_registry.model(context.selected_model)
        if not model_meta:
            raise ModelUnavailableError(f"Model '{context.selected_model}' is not registered.")

        if capability not in model_meta.capabilities:
            raise CapabilityUnavailableError(
                f"Model '{context.selected_model}' does not support '{capability.value}' capability."
            )

        provider_name = context.provider
        if not provider_name:
            # Match first registered provider supporting model name
            for name in self.provider_registry.list():
                inst = self.provider_registry.provider(name)
                if hasattr(inst, "supports_model") and inst.supports_model(context.selected_model):
                    provider_name = name
                    break

        if not provider_name:
            # Fallback based on model name prefix
            provider_name = context.selected_model.split("-")[0]

        provider = self.provider_registry.provider(provider_name)
        if not provider:
            raise ProviderNotFoundError(f"Provider '{provider_name}' not found.")

        # Check health
        health = self.provider_registry.health(provider_name)
        if health and not health.is_healthy:
            raise ProviderUnavailableError(f"Provider '{provider_name}' is unhealthy.")

        # Verify interface implementation
        if not self.factory.validate_provider(provider, capability):
            raise CapabilityUnavailableError(
                f"Provider '{provider_name}' does not implement interface for '{capability.value}'."
            )

        context.provider = provider_name
        return provider

    async def _execute(self, call_fn: Any, *args: Any, **kwargs: Any) -> Any:
        """Helper to run a method wrapping it inside retry and timeout policies."""
        attempt = 0
        while True:
            attempt += 1
            try:
                return await asyncio.wait_for(
                    call_fn(*args, **kwargs),
                    timeout=self.timeout_policy.timeout_seconds,
                )
            except asyncio.TimeoutError as err:
                if self.retry_policy.should_retry(err, attempt):
                    await asyncio.sleep(self.retry_policy.backoff_factor**attempt * 0.1)
                    continue
                raise GatewayTimeoutError("Gateway operation timed out.")
            except Exception as err:
                if self.retry_policy.should_retry(err, attempt):
                    await asyncio.sleep(self.retry_policy.backoff_factor**attempt * 0.1)
                    continue
                raise err

    async def chat(self, request: ChatRequest, **kwargs: Any) -> ChatResponse:
        """Orchestrates non-streaming chat completions."""
        context = RequestContext(selected_model=request.model)
        provider = self._resolve_provider(context, ProviderCapability.CHAT)

        res = await self._execute(provider.chat, request, **kwargs)
        return res

    async def stream_chat(
        self, request: ChatRequest, **kwargs: Any
    ) -> AsyncGenerator[StreamingChunk, None]:
        """Orchestrates token streaming chat completions."""
        context = RequestContext(selected_model=request.model)
        provider = self._resolve_provider(context, ProviderCapability.CHAT)

        # Execute stream retrieval from provider generator
        async for chunk in provider.stream_chat(request, **kwargs):
            yield chunk

    async def embeddings(self, request: EmbeddingRequest, **kwargs: Any) -> EmbeddingResponse:
        """Orchestrates text embeddings vector generations."""
        context = RequestContext(selected_model=request.model)
        provider = self._resolve_provider(context, ProviderCapability.EMBEDDINGS)

        res = await self._execute(provider.embed_text, request, **kwargs)
        return res

    async def image_generation(self, prompt: str, model: str, **kwargs: Any) -> str:
        """Orchestrates text-to-image completions."""
        context = RequestContext(selected_model=model)
        provider = self._resolve_provider(context, ProviderCapability.IMAGE)

        res = await self._execute(provider.generate_image, prompt, model, **kwargs)
        return res

    async def speech(self, text: str, model: str, **kwargs: Any) -> bytes:
        """Orchestrates text-to-speech audio synthesis (helper routing)."""
        context = RequestContext(selected_model=model)
        provider = self._resolve_provider(context, ProviderCapability.SPEECH)

        res = await self._execute(provider.text_to_speech, text, model, **kwargs)
        return res

    async def speech_to_text(self, audio_data: bytes, model: str, **kwargs: Any) -> str:
        """Orchestrates audio-to-text transcriptions."""
        context = RequestContext(selected_model=model)
        provider = self._resolve_provider(context, ProviderCapability.SPEECH)

        res = await self._execute(provider.speech_to_text, audio_data, model, **kwargs)
        return res

    async def text_to_speech(self, text: str, model: str, **kwargs: Any) -> bytes:
        """Orchestrates text-to-speech audio synthesis."""
        return await self.speech(text, model, **kwargs)

    async def vision(self, image_path: str, prompt: str, model: str, **kwargs: Any) -> str:
        """Orchestrates multimodal vision analysis."""
        context = RequestContext(selected_model=model)
        provider = self._resolve_provider(context, ProviderCapability.VISION)

        res = await self._execute(provider.analyze_image, image_path, prompt, model, **kwargs)
        return res
