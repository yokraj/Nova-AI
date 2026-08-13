"""Manager Facade coordinating Orchestration, Routing, Resource Scheduling, Benchmarking, and Execution.
"""

from typing import Any, AsyncGenerator, List, Optional
from app.ai.orchestrator.benchmark_engine import BenchmarkEngine
from app.ai.orchestrator.cache import OrchestratorCache
from app.ai.orchestrator.configuration import OrchestratorConfiguration
from app.ai.orchestrator.gpu_scheduler import GPUScheduler
from app.ai.orchestrator.health_monitor import HealthMonitor
from app.ai.orchestrator.intelligent_model_router import IntelligentModelRouter
from app.ai.orchestrator.metrics import OrchestratorMetricsTracker
from app.ai.orchestrator.model_installer import ModelInstaller
from app.ai.orchestrator.models import (
    ModelCategory,
    ModelSpec,
    OrchestratorRequest,
    OrchestratorResponse,
    RoutingContext,
    StreamTokenChunk,
)
from app.ai.orchestrator.prompt_optimizer import PromptOptimizer
from app.ai.orchestrator.provider_plugin_framework import ProviderPluginFactory
from app.ai.orchestrator.streaming_engine import StreamingEngine


class UniversalAIOrchestratorManager:
    """Manager facade controlling model discovery, registration, load/unload, routing, scheduling, streaming."""

    def __init__(self, config: Optional[OrchestratorConfiguration] = None) -> None:
        self.config = config or OrchestratorConfiguration()
        self.factory = ProviderPluginFactory()
        self.scheduler = GPUScheduler(
            total_vram_mb=self.config.max_vram_allocation_mb,
            total_ram_mb=self.config.max_ram_allocation_mb,
        )
        self.installer = ModelInstaller()
        self.benchmark_engine = BenchmarkEngine()
        self.router = IntelligentModelRouter(self.scheduler, self.benchmark_engine)
        self.prompt_optimizer = PromptOptimizer()
        self.streaming_engine = StreamingEngine(self.factory)
        self.health_monitor = HealthMonitor(self.scheduler)
        self.metrics_tracker = OrchestratorMetricsTracker()
        self.cache = OrchestratorCache(ttl_seconds=self.config.cache_ttl_seconds)

        self._registered_models: Dict[str, ModelSpec] = {
            "qwen3:8b": ModelSpec(model_id="qwen3:8b", name="Qwen3 8B Instruct", category=ModelCategory.REASONING),
            "deepseek-coder:6.7b": ModelSpec(model_id="deepseek-coder:6.7b", name="DeepSeek Coder 6.7B", category=ModelCategory.CODING),
            "qwen2.5-vl:7b": ModelSpec(model_id="qwen2.5-vl:7b", name="Qwen2.5 VL 7B", category=ModelCategory.VISION),
            "whisper-large-v3": ModelSpec(model_id="whisper-large-v3", name="Faster Whisper Large V3", category=ModelCategory.SPEECH),
            "piper-v1": ModelSpec(model_id="piper-v1", name="Piper Voice TTS", category=ModelCategory.TTS),
            "paddleocr-v4": ModelSpec(model_id="paddleocr-v4", name="PaddleOCR V4", category=ModelCategory.OCR),
            "bge-large-en-v1.5": ModelSpec(model_id="bge-large-en-v1.5", name="BGE Large En V1.5", category=ModelCategory.EMBEDDING),
            "nllb-200": ModelSpec(model_id="nllb-200", name="NLLB 200 Translation", category=ModelCategory.TRANSLATION),
        }

    async def execute_request(self, request: OrchestratorRequest) -> OrchestratorResponse:
        """Processes request through intelligent routing, cache check, GPU scheduler, prompt optimizer, and provider."""
        # 1. Routing Context & Decision
        routing_ctx = RoutingContext(
            request_id=request.request_id,
            prompt=request.prompt,
            category=request.category,
            context_tokens=len(request.prompt.split()),
        )
        decision = self.router.route_request(routing_ctx)
        self.metrics_tracker.record_routing_decision()

        target_model = request.model_override or decision.selected_model_id

        # 2. Check Cache
        if self.config.enable_cache and not request.stream:
            cached_data = self.cache.get(request.prompt, request.category.value, target_model)
            if cached_data is not None:
                self.metrics_tracker.record_inference(tokens=len(request.prompt.split()), latency_ms=2.0, cached=True)
                return OrchestratorResponse(
                    request_id=request.request_id,
                    model_id=target_model,
                    provider_type=decision.provider_type,
                    text_or_data=cached_data,
                    latency_ms=2.0,
                    cached=True,
                )

        # 3. Optimize Prompt
        optimized_prompt = request.prompt
        if self.config.enable_prompt_optimization:
            optimized_prompt = self.prompt_optimizer.optimize_prompt(request.prompt, request.category.value)

        req_to_send = OrchestratorRequest(
            request_id=request.request_id,
            prompt=optimized_prompt,
            category=request.category,
            model_override=target_model,
            inputs=request.inputs,
        )

        # 4. Prepare GPU & Resource
        await self.scheduler.prepare_resource(target_model, 4096)

        # 5. Execute via Provider
        provider = self.factory.get_provider(decision.provider_type.value)
        res = await provider.generate(req_to_send)

        # 6. Save Cache
        if self.config.enable_cache and res.text_or_data:
            self.cache.set(request.prompt, request.category.value, target_model, res.text_or_data)

        self.metrics_tracker.record_inference(tokens=len(request.prompt.split()) + 30, latency_ms=res.latency_ms)
        return res

    async def execute_stream(self, request: OrchestratorRequest) -> AsyncGenerator[StreamTokenChunk, None]:
        """Streams real-time token stream."""
        async for chunk in self.streaming_engine.stream_tokens(request):
            yield chunk

    def list_models(self) -> List[ModelSpec]:
        return list(self._registered_models.values())
