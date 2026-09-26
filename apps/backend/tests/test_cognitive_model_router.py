"""Phase 10E Test Suite — Native Local Model Router.

Tests:
1. Model registration and metadata profile management
2. Dynamic Ollama availability detection and server pinging
3. Workload type-based routing (CODING, REASONING, PLANNING, TOOL_SELECTION, etc.)
4. Context-budget constrained routing
5. Deterministic local fallback chain
6. Unavailable model detection and recovery
7. Structured-output requirement routing
8. VRAM and resource constraint filtering
9. Telemetry logging and routing decision recording
10. Zero-cost enforcement (cloud providers disabled by default)
11. LLMRuntime integration with LocalModelRouter
12. Real Ollama inference execution (with live qwen3:8b if online)
"""

import pytest

from app.ai.kernel.model_router import (
    CognitiveWorkloadType,
    LocalModelRouter,
    ModelProfile,
    RoutingConstraints,
)
from app.ai.runtime.llm_runtime import LLMRuntime
from app.ai.runtime.models import RuntimeRequest


class TestCognitiveModelRouter:
    """Test suite covering local model routing, health checks, fallbacks, and telemetry."""

    def test_1_model_registration(self):
        """1. Registers model profiles and retrieves stored metadata."""
        router = LocalModelRouter()
        profile = ModelProfile(
            model_id="test-coder:7b",
            name="Test Coder Model",
            provider_type="ollama",
            context_window=32768,
            code_score=0.95,
            is_healthy=True,
            priority=12,
        )
        router.register_model(profile)

        assert "test-coder:7b" in router.registered_models
        assert router.registered_models["test-coder:7b"].code_score == 0.95

    def test_2_availability_detection(self):
        """2. Detects live Ollama server status and updates health profile."""
        router = LocalModelRouter()
        is_online, models = router.check_ollama_server_health()

        assert isinstance(is_online, bool)
        assert isinstance(models, list)
        if is_online:
            assert len(models) > 0

    @pytest.mark.asyncio
    async def test_3_routing_by_workload_type(self):
        """3. Routes requests to optimal model profiles based on cognitive workload type."""
        router = LocalModelRouter()
        # Seed custom profiles
        router.register_model(
            ModelProfile(
                model_id="spec-coder:7b",
                name="Specialized Coder",
                code_score=0.99,
                reasoning_score=0.70,
                is_healthy=True,
                priority=15,
            )
        )

        dec_code = await router.route_workload(CognitiveWorkloadType.CODE_GENERATION)
        assert dec_code.selected_model_id == "spec-coder:7b"
        assert dec_code.workload_type == CognitiveWorkloadType.CODE_GENERATION
        assert not dec_code.fallback_used

    @pytest.mark.asyncio
    async def test_4_context_budget_routing(self):
        """4. Rejects models that do not meet minimum context token budgets."""
        router = LocalModelRouter()
        # Register a small context model vs large context model
        router.register_model(
            ModelProfile(
                model_id="small-ctx:3b",
                name="Small Context Model",
                context_window=4096,
                reasoning_score=0.95,
                is_healthy=True,
                priority=20,
            )
        )
        router.register_model(
            ModelProfile(
                model_id="large-ctx:8b",
                name="Large Context Model",
                context_window=32768,
                reasoning_score=0.90,
                is_healthy=True,
                priority=10,
            )
        )

        constraints = RoutingConstraints(min_context_tokens=16384)
        dec = await router.route_workload(CognitiveWorkloadType.REASONING, constraints)

        assert dec.selected_model_id != "small-ctx:3b"
        assert dec.selected_model_id in ["large-ctx:8b", "qwen3:8b"]

    @pytest.mark.asyncio
    async def test_5_deterministic_fallback(self):
        """5. Triggers deterministic local fallback when primary model is unhealthy or missing."""
        router = LocalModelRouter()
        # Mark all specialized models as unhealthy
        for p in router.registered_models.values():
            p.is_healthy = False

        # Add a healthy fallback profile
        router.register_model(
            ModelProfile(
                model_id="fallback-local:8b",
                name="Healthy Fallback Model",
                is_healthy=True,
                priority=100,
            )
        )

        constraints = RoutingConstraints(preferred_model_id="unhealthy-model:7b")
        dec = await router.route_workload(CognitiveWorkloadType.PLANNING, constraints)

        assert dec.fallback_used
        assert dec.selected_model_id == "fallback-local:8b"
        assert dec.fallback_reason is not None

    @pytest.mark.asyncio
    async def test_6_unavailable_model_handling(self):
        """6. Gracefully handles requests when preferred model is completely unavailable."""
        router = LocalModelRouter()
        constraints = RoutingConstraints(preferred_model_id="nonexistent-model-xyz")

        dec = await router.route_workload(CognitiveWorkloadType.REASONING, constraints)
        assert dec.selected_model_id != "nonexistent-model-xyz"
        assert dec.success

    @pytest.mark.asyncio
    async def test_7_structured_output_routing(self):
        """7. Enforces structured-output capability requirement."""
        router = LocalModelRouter()
        router.register_model(
            ModelProfile(
                model_id="no-json-model",
                name="Unstructured Model",
                structured_output_score=0.2,
                is_healthy=True,
                priority=50,
            )
        )
        router.register_model(
            ModelProfile(
                model_id="json-model",
                name="Structured Model",
                structured_output_score=0.95,
                is_healthy=True,
                priority=10,
            )
        )

        constraints = RoutingConstraints(require_structured_output=True)
        dec = await router.route_workload(CognitiveWorkloadType.TASK_DECOMPOSITION, constraints)

        assert dec.selected_model_id == "json-model" or "qwen" in dec.selected_model_id

    @pytest.mark.asyncio
    async def test_8_resource_constraints_vram(self):
        """8. Filters candidates based on maximum VRAM memory budgets."""
        router = LocalModelRouter()
        router.register_model(
            ModelProfile(
                model_id="heavy-vram:70b",
                name="Heavy 70B Model",
                vram_mb=40000,
                reasoning_score=0.99,
                is_healthy=True,
                priority=100,
            )
        )

        constraints = RoutingConstraints(max_vram_mb=8000)
        dec = await router.route_workload(CognitiveWorkloadType.REASONING, constraints)

        assert dec.selected_model_id != "heavy-vram:70b"

    @pytest.mark.asyncio
    async def test_9_telemetry_recording(self):
        """9. Records detailed decision telemetry in history log."""
        router = LocalModelRouter()
        router.clear_telemetry_history()

        _ = await router.route_workload(CognitiveWorkloadType.TOOL_SELECTION)
        _ = await router.route_workload(CognitiveWorkloadType.CODE_GENERATION)

        history = router.get_telemetry_history()
        assert len(history) == 2
        assert history[0].workload_type == CognitiveWorkloadType.TOOL_SELECTION
        assert history[1].workload_type == CognitiveWorkloadType.CODE_GENERATION

    def test_10_zero_cost_local_default(self):
        """10. Confirms cloud fallback is disabled by default for zero-cost enforcement."""
        constraints = RoutingConstraints()
        assert not constraints.allow_cloud_fallback

    @pytest.mark.asyncio
    async def test_11_llm_runtime_integration(self):
        """11. Verifies LLMRuntime utilizes LocalModelRouter for inference requests."""
        router = LocalModelRouter()
        runtime = LLMRuntime(router=router)

        req = RuntimeRequest(prompt="Write a python script to add a cube in Blender", max_tokens=100)
        res = await runtime.generate(req)

        assert res.model_id is not None
        telemetry = router.get_telemetry_history()
        assert len(telemetry) >= 1
        assert telemetry[-1].workload_type == CognitiveWorkloadType.CODE_GENERATION

    @pytest.mark.asyncio
    async def test_12_real_ollama_inference_execution(self):
        """12. Executes real local inference against installed Ollama model (qwen3:8b)."""
        router = LocalModelRouter()
        is_online, installed = router.check_ollama_server_health()

        if not is_online:
            pytest.skip("Local Ollama server is offline")

        runtime = LLMRuntime(router=router)
        req = RuntimeRequest(
            prompt="Reply with exact phrase: 'NOVA_LOCAL_ROUTER_VERIFIED'",
            max_tokens=50,
            temperature=0.1,
        )

        res = await runtime.generate(req)
        assert res.text_or_data is not None
        assert len(res.text_or_data) > 0
        assert res.token_usage["total_tokens"] > 0
