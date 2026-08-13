"""Unit and integration tests for M3.4.18 Universal Multi-Model AI Ecosystem & Intelligent AI Orchestrator.
"""

import pytest
from app.ai.orchestrator.engine import UniversalAIOrchestratorEngine
from app.ai.orchestrator.gpu_scheduler import GPUScheduler
from app.ai.orchestrator.intelligent_model_router import IntelligentModelRouter
from app.ai.orchestrator.manager import UniversalAIOrchestratorManager
from app.ai.orchestrator.model_installer import ModelInstaller
from app.ai.orchestrator.benchmark_engine import BenchmarkEngine
from app.ai.orchestrator.models import ModelCategory, RoutingContext
from app.ai.orchestrator.prompt_optimizer import PromptOptimizer
from app.ai.orchestrator.provider_plugin_framework import ProviderPluginFactory


@pytest.mark.anyio
async def test_provider_plugin_factory():
    factory = ProviderPluginFactory()
    providers = factory.list_providers()
    assert "ollama" in providers
    assert "whisper" in providers
    assert "piper" in providers
    assert "paddle_ocr" in providers

    ollama = factory.get_provider("ollama")
    assert ollama.provider_name == "ollama"


@pytest.mark.anyio
async def test_gpu_scheduler_telemetry_and_oom_prevention():
    scheduler = GPUScheduler(total_vram_mb=24576)
    telemetry = scheduler.get_telemetry()
    assert telemetry.vram_total_mb == 24576.0
    assert len(telemetry.active_models_loaded) >= 1

    ok = await scheduler.prepare_resource("qwen3:8b", 4096)
    assert ok is True


@pytest.mark.anyio
async def test_intelligent_model_router_10_categories():
    scheduler = GPUScheduler()
    benchmarks = BenchmarkEngine()
    router = IntelligentModelRouter(scheduler, benchmarks)

    code_route = router.route_request(RoutingContext(prompt="def add(a, b):", category=ModelCategory.CODING))
    assert code_route.selected_model_id == "deepseek-coder:6.7b"

    reason_route = router.route_request(RoutingContext(prompt="Analyze system architecture", category=ModelCategory.REASONING))
    assert reason_route.selected_model_id == "qwen3:8b"

    vis_route = router.route_request(RoutingContext(prompt="Find submit button", category=ModelCategory.VISION))
    assert vis_route.selected_model_id == "qwen2.5-vl:7b"

    emb_route = router.route_request(RoutingContext(prompt="semantic text", category=ModelCategory.EMBEDDING))
    assert emb_route.selected_model_id == "bge-large-en-v1.5"


@pytest.mark.anyio
async def test_model_installer_and_benchmark_engine():
    installer = ModelInstaller()
    has_model = await installer.check_missing_model("qwen3:8b")
    assert has_model is True

    progress = await installer.install_model("custom_model:8b")
    assert progress.checksum_verified is True

    benchmark = BenchmarkEngine()
    score = await benchmark.benchmark_model("qwen3:8b")
    assert score.overall_score >= 0.8


@pytest.mark.anyio
async def test_prompt_optimizer():
    optimizer = PromptOptimizer()
    opt = optimizer.optimize_prompt("Write a test function", "coding")
    assert "Principal Software Engineer" in opt


@pytest.mark.anyio
async def test_universal_ai_orchestrator_engine_facade():
    engine = UniversalAIOrchestratorEngine()

    chat_res = await engine.chat("Hello Nova AI Orchestrator")
    assert chat_res.text_or_data != ""

    reason_res = await engine.reason("Derive optimal system architecture")
    assert reason_res.text_or_data != ""

    code_res = await engine.code("def multiply(a, b):")
    assert code_res.text_or_data != ""

    vis_res = await engine.vision("screenshot.png", prompt="Find button")
    assert vis_res.text_or_data != ""

    trans_res = await engine.translate("Hello world", target_lang="es")
    assert trans_res.text_or_data != ""

    health = engine.health_check()
    assert health.is_healthy is True
