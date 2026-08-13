"""Resilient Offline Simulation Provider Adapter for Universal AI Orchestrator.
"""

from typing import Any, AsyncGenerator, Dict
from app.ai.orchestrator.interfaces import IProviderPlugin
from app.ai.orchestrator.models import (
    ModelCategory,
    OrchestratorRequest,
    OrchestratorResponse,
    ProviderType,
    StreamTokenChunk,
)


class MockProviderAdapter(IProviderPlugin):
    """Fallback offline simulation provider for offline/test environments."""

    @property
    def provider_name(self) -> str:
        return "mock_simulator"

    async def is_available(self) -> bool:
        return True

    async def generate(self, request: OrchestratorRequest) -> OrchestratorResponse:
        model_id = request.model_override or "qwen3:8b"
        prompt_lower = request.prompt.lower()

        if "code" in prompt_lower or "def " in prompt_lower:
            text = f"```python\n# Simulated Code by {model_id}\ndef orchestrator_demo():\n    return 'Mock Success'\n```"
        elif "reason" in prompt_lower or "plan" in prompt_lower:
            text = f"[Mock Orchestrator - {model_id}] 1. Verified task.\n2. Executed reasoning graph.\n3. Complete."
        else:
            text = f"[Mock Orchestrator - {model_id}] Response to: {request.prompt[:100]}"

        return OrchestratorResponse(
            request_id=request.request_id,
            model_id=model_id,
            provider_type=ProviderType.MOCK_SIMULATOR,
            text_or_data=text,
            latency_ms=25.0,
            cached=False,
        )

    async def generate_stream(self, request: OrchestratorRequest) -> AsyncGenerator[StreamTokenChunk, None]:
        model_id = request.model_override or "qwen3:8b"
        tokens = f"[Mock Stream Token] Response to {request.prompt[:60]}".split()
        for idx, t in enumerate(tokens):
            yield StreamTokenChunk(
                request_id=request.request_id,
                model_id=model_id,
                delta_text=t + (" " if idx < len(tokens) - 1 else ""),
                token_index=idx,
                is_final=(idx == len(tokens) - 1),
            )
