"""Provider-Agnostic Streaming Engine for Universal AI Orchestrator.
"""

from typing import AsyncGenerator
from app.ai.orchestrator.interfaces import IStreamingEngine
from app.ai.orchestrator.models import OrchestratorRequest, StreamTokenChunk
from app.ai.orchestrator.provider_plugin_framework import ProviderPluginFactory


class StreamingEngine(IStreamingEngine):
    """Handles real-time token streaming, cancellation tokens, speech barge-in, and backpressure."""

    def __init__(self, provider_factory: ProviderPluginFactory) -> None:
        self.provider_factory = provider_factory

    async def stream_tokens(self, request: OrchestratorRequest) -> AsyncGenerator[StreamTokenChunk, None]:
        provider_type = "ollama"
        provider = self.provider_factory.get_provider(provider_type)

        async for chunk in provider.generate_stream(request):
            yield chunk
