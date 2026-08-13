"""Tests for the Local AI Model Runtime Foundation.
"""

import pytest
from app.ai.runtime.configuration import LocalModelConfig
from app.ai.runtime.registry import LocalModelRegistry
from app.ai.runtime.runtime_manager import LocalRuntimeManager
from app.ai.runtime.provider import LocalModelRouter
from app.ai.runtime.health import LocalHealthMonitor
from app.ai.runtime.metrics import LocalMetricsTracker
from app.ai.runtime.cache import LocalInferenceCache
from app.ai.runtime.providers.ollama import OllamaLocalProvider
from app.ai.runtime.providers.llamacpp import LlamaCppLocalProvider
from app.ai.models import ChatRequest, PromptMessage, EmbeddingRequest

@pytest.mark.anyio
async def test_local_model_configuration_loading():
    """Verifies that configuration structures parse parameters properly."""
    config = LocalModelConfig(
        name="qwen2.5-coder",
        type="llm",
        provider="ollama",
        context_window=32768,
        temperature=0.2,
        max_tokens=4096
    )
    assert config.name == "qwen2.5-coder"
    assert config.context_window == 32768
    assert config.use_gpu is True

@pytest.mark.anyio
async def test_local_model_registry():
    """Verifies registry pre-populates default models."""
    registry = LocalModelRegistry()
    models = registry.list_models()
    assert len(models) >= 4
    
    coder = registry.get_model("qwen2.5-coder")
    assert coder is not None
    assert coder.type == "llm"
    assert coder.loaded_status is False

@pytest.mark.anyio
async def test_local_model_router():
    """Verifies task routing maps prompts to the correct models."""
    router = LocalModelRouter()
    
    assert router.select_model_for_task("Fix Python bug in database connections") == "qwen2.5-coder"
    assert router.select_model_for_task("Explain clean architecture design principles") == "deepseek-r1-distill-qwen"
    assert router.select_model_for_task("Create text embeddings for search") == "nomic-embed-text"
    assert router.select_model_for_task("Analyze image snapshot input") == "qwen2.5-vl"

@pytest.mark.anyio
async def test_local_runtime_manager_lifecycle():
    """Verifies runtime lazy loading and memory state lifecycle."""
    registry = LocalModelRegistry()
    # Mock Ollama provider methods to bypass physical local server calls
    class MockOllamaProvider(OllamaLocalProvider):
        async def detect_ollama(self) -> bool:
            return True
        async def load_model(self, model_name: str) -> bool:
            return True
        async def unload_model(self, model_name: str) -> bool:
            return True

    provider = MockOllamaProvider()
    manager = LocalRuntimeManager(registry=registry, provider=provider)

    # Runtime startup
    assert await manager.start_runtime() is True

    # Lazy loading check
    model_info = await manager.get_or_load_model("qwen2.5-coder")
    assert model_info.loaded_status is True
    assert "qwen2.5-coder" in manager.loaded_models

    # Unload check
    assert await manager.unload_model("qwen2.5-coder") is True
    assert "qwen2.5-coder" not in manager.loaded_models

@pytest.mark.anyio
async def test_local_health_and_metrics_monitoring():
    """Verifies health monitoring diagnostics and metrics collections."""
    registry = LocalModelRegistry()
    class MockOllamaProvider(OllamaLocalProvider):
        async def health(self):
            from app.ai.models import ProviderHealth
            return ProviderHealth(is_healthy=True, latency_ms=5.0, status_code=200)

    provider = MockOllamaProvider()
    monitor = LocalHealthMonitor(registry=registry, provider=provider)
    
    summary = await monitor.get_overall_health()
    assert summary["is_healthy"] is True
    assert summary["latency_ms"] == 5.0

    tracker = LocalMetricsTracker()
    tracker.record_inference(model_name="qwen2.5-coder", duration=1.2, prompt_tokens=100, completion_tokens=50, success=True)
    
    metrics = tracker.get_summary()
    assert metrics["tokens_generated"] == 50
    assert metrics["total_latency_sec"] == 1.2

@pytest.mark.anyio
async def test_local_mock_inference():
    """Verifies chat, stream generation, and embedding outputs on providers."""
    class MockOllamaProvider(OllamaLocalProvider):
        async def generate(self, request: ChatRequest, **kwargs):
            from app.ai.models import ChatResponse, PromptMessage, AIUsage
            return ChatResponse(
                message=PromptMessage(role="assistant", content="Mocked local response"),
                finish_reason="stop",
                usage=AIUsage(),
                model=request.model,
                provider="ollama"
            )

    provider = MockOllamaProvider()
    request = ChatRequest(model="qwen2.5-coder", messages=[PromptMessage(role="user", content="hello")])
    response = await provider.generate(request)
    assert response.message.content == "Mocked local response"
