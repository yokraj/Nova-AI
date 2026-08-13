"""Unit and integration tests for M3.4.17 Real AI Runtime Integration & Unified Model Execution.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../apps/backend")))

from app.ai.models.providers.ollama_provider import OllamaProvider
from app.ai.models.model_registry import UniversalModelRegistry
from app.ai.router.model_selector import ModelSelector
from app.ai.router.models import RoutingRequest, TaskType
from app.ai.runtime.runtime_engine import UniversalAIRuntimeEngine
from app.ai.runtime.runtime_monitor import RuntimeMonitor
from app.ai.runtime.resource_scheduler import ResourceScheduler


@pytest.mark.anyio
async def test_ollama_provider_health_and_generate():
    provider = OllamaProvider()
    health = await provider.health_check()
    assert "status" in health

    from app.ai.models.models import GenerationRequest
    res = await provider.generate(GenerationRequest(prompt="Hello Nova Real AI", model_id="qwen3:8b"))
    assert res.text != ""
    assert res.model_id == "qwen3:8b"


@pytest.mark.anyio
async def test_ollama_provider_embeddings_and_vision():
    provider = OllamaProvider()
    from app.ai.models.models import EmbeddingRequest, VisionRequest
    emb_res = await provider.embed(EmbeddingRequest(text_list=["Nova AI", "Local LLM"]))
    assert len(emb_res.embeddings) == 2
    assert emb_res.dimensions == 768

    vis_res = await provider.process_vision(VisionRequest(prompt="Find button", image_bytes_or_path="screenshot.png"))
    assert vis_res.description != ""


@pytest.mark.anyio
async def test_universal_model_registry_discovery():
    registry = UniversalModelRegistry()
    models = registry.list_models()
    assert len(models) >= 5

    discovered = await registry.discover_ollama_capabilities([
        {"name": "qwen3:8b", "size": 5200000000},
        {"name": "deepseek-coder:6.7b", "size": 4200000000},
    ])
    assert len(discovered) == 2


@pytest.mark.anyio
async def test_intelligent_model_selector_routing():
    selector = ModelSelector()
    
    code_dec = selector.select_best_model(RoutingRequest(request_id="req_01", prompt="Write FastAPI server", task_type=TaskType.CODE_GENERATION))
    assert code_dec.selected_model == "deepseek-coder:6.7b"

    reason_dec = selector.select_best_model(RoutingRequest(request_id="req_02", prompt="Analyze architecture", task_type=TaskType.REASONING))
    assert reason_dec.selected_model == "qwen3:8b"

    vis_dec = selector.select_best_model(RoutingRequest(request_id="req_03", prompt="Analyze screenshot", task_type=TaskType.VISION))
    assert vis_dec.selected_model == "qwen2.5-vl:7b"


@pytest.mark.anyio
async def test_universal_ai_runtime_engine():
    engine = UniversalAIRuntimeEngine()
    
    chat_res = await engine.chat("Hello Nova AI OS", model_id="qwen3:8b")
    assert chat_res.text_or_data != ""

    reason_res = await engine.reason("Derive optimal system architecture")
    assert reason_res.text_or_data != ""

    code_res = await engine.code("def calculate_sum(a, b):")
    assert code_res.text_or_data != ""

    emb_res = await engine.embed(["test vector"])
    assert isinstance(emb_res.text_or_data, dict) or isinstance(emb_res.text_or_data, list)


@pytest.mark.anyio
async def test_runtime_monitor_diagnostics():
    scheduler = ResourceScheduler()
    monitor = RuntimeMonitor(scheduler)
    diag = monitor.get_runtime_diagnostics()
    assert diag["is_healthy"] is True
    assert "qwen3:8b" in diag["loaded_models"]
    assert diag["streaming_health"] == "OPTIMAL"
