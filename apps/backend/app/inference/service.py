"""Inference Service Layer Module.

Provides decoupled asynchronous business service abstractions:
InferenceService, GatewayService, ModelService, StreamingService, and BenchmarkService.
"""

from typing import Any, AsyncGenerator, Dict, List, Optional
import time
import structlog

from app.inference.repository import InferenceRepository
from app.inference.model_registry import ModelRegistry
from app.inference.provider_manager import ProviderManager
from app.inference.provider_router import ProviderRouter
from app.inference.model_router import ModelRouter
from app.inference.gpu_scheduler import GPUScheduler
from app.inference.streaming import StreamingEngine
from app.inference.benchmark import InferenceBenchmarker
from app.inference.health import InferenceHealthChecker
from app.inference.statistics import InferenceStatisticsTracker
from app.inference.schemas import (
    ChatInferenceRequest,
    ChatInferenceResponse,
    TaskClassificationRequest,
    TaskClassificationResponse,
    ModelCatalogItem,
    InferenceHealthResponse,
    InferenceStatisticsResponse,
)

logger = structlog.get_logger(__name__)


class InferenceService:
    """Business service handling non-streaming chat inference execution."""

    def __init__(self, repository: InferenceRepository) -> None:
        self.repository = repository
        self.model_router = ModelRouter()
        self.provider_router = ProviderRouter()
        self.gpu_scheduler = GPUScheduler()
        self.stats_tracker = InferenceStatisticsTracker()
        logger.info("inference_service_initialized")

    async def execute_chat(self, request: ChatInferenceRequest) -> ChatInferenceResponse:
        """Executes chat completion request through routing, GPU scheduling, and provider execution."""
        t0 = time.perf_counter()

        # 1. Model Routing & Capability Detection
        route_res = self.model_router.route_request(
            request.prompt, user_model=request.model, user_provider=request.provider
        )

        model_name = route_res["selected_model"]
        provider_name = route_res["selected_provider"]

        # 2. GPU Scheduling Allocation
        gpu_res = self.gpu_scheduler.allocate_gpu(vram_required_mb=4096)

        # 3. Provider Backend Execution
        dispatch_res = await self.provider_router.dispatch_request(
            provider=provider_name,
            model=model_name,
            prompt=request.prompt,
            system_prompt=request.system_prompt,
        )

        # 4. Release GPU Allocation
        if not gpu_res["fallback_to_cpu"]:
            self.gpu_scheduler.release_gpu(gpu_res["gpu_id"], vram_released_mb=4096)

        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        # 5. Persist Log
        log_record = await self.repository.save_request_log(
            prompt=request.prompt,
            model_name=model_name,
            provider=provider_name,
            task_category=route_res["task_category"],
            prompt_tokens=dispatch_res["prompt_tokens"],
            completion_tokens=dispatch_res["completion_tokens"],
            latency_ms=latency_ms,
        )

        self.stats_tracker.record_inference(
            prompt_tokens=dispatch_res["prompt_tokens"],
            completion_tokens=dispatch_res["completion_tokens"],
            ttft_ms=15.0,
        )

        return ChatInferenceResponse(
            request_id=log_record.id,
            content=dispatch_res["content"],
            model=model_name,
            provider=provider_name,
            task_category=route_res["task_category"],
            prompt_tokens=dispatch_res["prompt_tokens"],
            completion_tokens=dispatch_res["completion_tokens"],
            total_tokens=dispatch_res["prompt_tokens"] + dispatch_res["completion_tokens"],
            latency_ms=latency_ms,
            created_at=log_record.created_at,
        )


class GatewayService:
    """Business service handling task classification and gateway metadata."""

    def __init__(self, repository: InferenceRepository) -> None:
        self.repository = repository
        self.model_router = ModelRouter()
        logger.info("gateway_service_initialized")

    def classify_task(self, request: TaskClassificationRequest) -> TaskClassificationResponse:
        """Classifies task intent category."""
        res = self.model_router.route_request(request.prompt)
        return TaskClassificationResponse(
            task_category=res["task_category"],
            detected_capabilities=res["detected_capabilities"],
            recommended_model=res["selected_model"],
            confidence=0.95,
        )


class ModelService:
    """Business service handling model catalog and provider management."""

    def __init__(self, repository: InferenceRepository) -> None:
        self.repository = repository
        self.model_registry = ModelRegistry()
        self.provider_manager = ProviderManager()
        logger.info("model_service_initialized")

    def list_models(self) -> List[ModelCatalogItem]:
        """Lists registered models."""
        return self.model_registry.list_models()

    def list_providers(self) -> List[Dict[str, Any]]:
        """Lists registered providers."""
        return self.provider_manager.list_providers()


class StreamingService:
    """Business service handling SSE token streaming."""

    def __init__(self, repository: InferenceRepository) -> None:
        self.repository = repository
        self.streaming_engine = StreamingEngine()
        logger.info("streaming_service_initialized")

    async def stream_chat(
        self, prompt: str, model: str = "llama3.2", provider: str = "ollama"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generates streaming tokens."""
        async for chunk in self.streaming_engine.stream_tokens(prompt, model, provider):
            yield chunk


class BenchmarkService:
    """Business service handling gateway benchmarking, health, and statistics."""

    def __init__(self, repository: InferenceRepository) -> None:
        self.repository = repository
        self.benchmarker = InferenceBenchmarker()
        self.health_checker = InferenceHealthChecker()
        self.stats_tracker = InferenceStatisticsTracker()
        logger.info("benchmark_service_initialized")

    async def get_statistics(self) -> InferenceStatisticsResponse:
        """Returns gateway telemetry statistics."""
        count = await self.repository.count_requests()
        self.stats_tracker.total_requests = count
        return self.stats_tracker.get_statistics()

    async def check_health(self) -> InferenceHealthResponse:
        """Runs gateway diagnostic health checks."""
        return self.health_checker.run_health_checks()
