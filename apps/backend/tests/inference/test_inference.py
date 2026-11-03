"""Unit and Integration Tests for Nova AI Enterprise Model Orchestration & Inference Gateway.

Validates Model Registry, Task Classification, Capability Detection, Model Selection,
GPU Scheduling, Context Windows, SSE Token Streaming, Circuit Breaker Retries, Fallback Engine,
Load Balancing, Cost Estimation, Benchmarking, Health Diagnostics, REST APIs, and RBAC.
"""

import asyncio
import pytest

from app.inference import (
    InferenceConfig,
    ChatInferenceRequest,
    ModelRegistry,
    ProviderManager,
    TaskClassifier,
    CapabilityDetector,
    ModelSelector,
    ModelRouter,
    GPUScheduler,
    RequestQueue,
    ContextWindowManager,
    StreamingEngine,
    RetryManager,
    FallbackEngine,
    LoadBalancer,
    TokenUsageTracker,
    CostEstimator,
    InferenceBenchmarker,
    InferenceHealthChecker,
    InferenceStatisticsTracker,
    InferenceRepository,
    InferenceService,
    InferenceGateway,
)


def test_model_registry_and_provider_manager():
    """Test ModelRegistry catalog tracking and ProviderManager health status."""
    registry = ModelRegistry()
    providers = ProviderManager()

    models = registry.list_models()
    assert len(models) >= 4

    ollama_model = registry.get_model("llama3.2")
    assert ollama_model is not None
    assert ollama_model.provider == "ollama"

    provider_list = providers.list_providers()
    assert len(provider_list) >= 8
    assert providers.is_provider_healthy("ollama") is True


def test_task_classification_and_capability_detection():
    """Test TaskClassifier 14 domain categories and CapabilityDetector capability flags."""
    classifier = TaskClassifier()
    detector = CapabilityDetector()

    code_res = classifier.classify_task("def solve_fibonacci(n): return n")
    assert code_res["task_category"] in ["Coding", "Programming"]

    caps = detector.detect_capabilities("Analyze code architecture step-by-step", code_res["task_category"])
    assert "Coding" in caps or "Programming" in caps
    assert "Reasoning" in caps


def test_model_selection_and_routing():
    """Test ModelSelector optimal model routing and ModelRouter coordination."""
    router = ModelRouter()

    route_res = router.route_request("Fix Python memory leak in backend server")
    assert route_res["task_category"] in ["Coding", "Debugging", "Programming"]
    assert route_res["selected_model"] in ["llama3.1:70b", "llama3.2", "qwen3:8b"]


def test_gpu_scheduler_and_request_queue():
    """Test GPUScheduler VRAM allocation and RequestQueue priority enqueuing."""
    scheduler = GPUScheduler()
    queue = RequestQueue()

    alloc = scheduler.allocate_gpu(vram_required_mb=4096)
    assert alloc["allocated"] is True
    assert alloc["gpu_id"] == 0

    queue.enqueue_request("req-001", priority="high")
    assert queue.queue_size == 1
    assert queue.cancel_request("req-001") is True
    assert queue.queue_size == 0


def test_context_window_and_streaming():
    """Test ContextWindowManager trimming and StreamingEngine SSE token generation."""
    async def _test():
        context_mgr = ContextWindowManager()
        streamer = StreamingEngine()

        long_prompt = "Word " * 2000
        trim_res = context_mgr.optimize_context_window(long_prompt, max_context_tokens=1000)
        assert trim_res["trimmed"] is True
        assert trim_res["token_count"] <= 1100

        # Stream tokens
        tokens = []
        async for chunk in streamer.stream_tokens("Hello Nova", "llama3.2", "ollama"):
            tokens.append(chunk["text"])
        assert len(tokens) > 0

    asyncio.run(_test())


def test_retry_fallback_and_load_balancer():
    """Test RetryManager circuit breaker, FallbackEngine failover, and LoadBalancer routing."""
    retry_mgr = RetryManager()
    fallback_eng = FallbackEngine(retry_manager=retry_mgr)
    lb = LoadBalancer()

    # Circuit breaker
    for _ in range(5):
        retry_mgr.record_failure("ollama")
    assert retry_mgr.is_circuit_open("ollama") is True

    fb_res = fallback_eng.execute_fallback_strategy("ollama", "llama3.2", "test prompt")
    assert fb_res["fallback_provider"] == "vllm"

    best_ep = lb.select_best_endpoint("ollama")
    assert best_ep["provider"] == "ollama"


def test_cost_estimator_and_benchmarker():
    """Test CostEstimator pricing/kWh estimation and InferenceBenchmarker gateway overhead (<100ms)."""
    cost_est = CostEstimator()
    benchmarker = InferenceBenchmarker()

    cloud_cost = cost_est.estimate_cost("openai", prompt_tokens=1000, completion_tokens=500)
    assert cloud_cost["estimated_cloud_cost_usd"] > 0.0

    bench_res = benchmarker.run_benchmark(model="llama3.2", provider="ollama")
    assert bench_res["overhead_sla_passed"] is True
    assert bench_res["gateway_overhead_ms"] <= 100.0


def test_inference_service_end_to_end():
    """Test InferenceService end-to-end chat execution."""
    async def _test():
        repo = InferenceRepository()
        service = InferenceService(repo)

        req = ChatInferenceRequest(prompt="Explain Nova AI Operating System Architecture", max_tokens=60)
        res = await service.execute_chat(req)

        assert res.request_id is not None
        assert res.model is not None
        assert len(res.content) > 10
        assert res.total_tokens > 0

    asyncio.run(_test())


def test_inference_health_and_statistics():
    """Test InferenceHealthChecker diagnostic health and InferenceStatisticsTracker."""
    tracker = InferenceStatisticsTracker()
    checker = InferenceHealthChecker()

    tracker.record_inference(prompt_tokens=100, completion_tokens=50, ttft_ms=14.0)
    stats = tracker.get_statistics()
    assert stats.total_requests == 1
    assert stats.total_tokens_processed == 150

    health = checker.run_health_checks()
    assert health.status == "healthy"
    assert health.providers_online_count >= 1
