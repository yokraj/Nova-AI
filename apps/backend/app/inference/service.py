"""Inference Service Layer Module for Nova AI Core Intelligence.

Provides decoupled asynchronous business service abstractions:
InferenceService, GatewayService, ModelService, StreamingService, and BenchmarkService,
with deterministic math calculation, response verification, and multi-turn chat memory.
"""

import asyncio
from typing import Any, AsyncGenerator, Dict, List, Optional, cast
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
from app.intelligence.deterministic_tools import DeterministicCalculator
from app.intelligence.response_validator import ResponseValidator
from app.intelligence.document_resolver import DocumentContextResolver
from app.intelligence.agent_execution_engine import AgentExecutionEngine, TaskIntent
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
        self.calculator = DeterministicCalculator()
        self.response_validator = ResponseValidator()
        self.document_resolver = DocumentContextResolver()
        self.agent_engine = AgentExecutionEngine()
        logger.info("inference_service_initialized")

    async def execute_chat(self, request: ChatInferenceRequest) -> ChatInferenceResponse:
        """Executes chat completion request through deterministic routing, GPU scheduling, and provider execution."""
        t0 = time.perf_counter()

        # 0. Check Unified Agent Execution Engine for operational tasks and security checks
        task_analysis = self.agent_engine.understand_task(request.prompt)
        intent = task_analysis["intent"]

        if intent in (
            TaskIntent.SECURITY_VIOLATION,
            TaskIntent.MULTI_STEP_TASK,
            TaskIntent.DESKTOP_OPERATION,
            TaskIntent.FILE_OPERATION,
            TaskIntent.CODE_ANALYSIS,
        ):
            plan = self.agent_engine.create_plan(request.prompt, task_analysis)
            report = await self.agent_engine.execute_plan(plan)
            latency_ms = round((time.perf_counter() - t0) * 1000, 2)
            content = report.final_output
            p_tokens = int(len(request.prompt.split()) * 1.3)
            c_tokens = int(len(content.split()) * 1.3)

            category_map = {
                TaskIntent.SECURITY_VIOLATION: "Security",
                TaskIntent.MULTI_STEP_TASK: "Multi-Step Automation",
                TaskIntent.DESKTOP_OPERATION: "Desktop Automation",
                TaskIntent.FILE_OPERATION: "File Operations",
                TaskIntent.CODE_ANALYSIS: "Code Intelligence",
            }
            task_category = category_map.get(intent, "Agent Execution")

            log_record = await self.repository.save_request_log(
                prompt=request.prompt,
                model_name="unified_agent_execution_engine",
                provider="local_engine",
                task_category=task_category,
                prompt_tokens=p_tokens,
                completion_tokens=c_tokens,
                latency_ms=latency_ms,
            )

            self.stats_tracker.record_inference(
                prompt_tokens=p_tokens,
                completion_tokens=c_tokens,
                ttft_ms=1.0,
            )

            return ChatInferenceResponse(
                request_id=str(log_record.id),
                content=content,
                model="unified_agent_execution_engine",
                provider="local_engine",
                task_category=task_category,
                prompt_tokens=p_tokens,
                completion_tokens=c_tokens,
                total_tokens=p_tokens + c_tokens,
                latency_ms=latency_ms,
                created_at=cast(Any, log_record.created_at),
                is_deterministic=True,
                verification={
                    "valid": report.verified,
                    "method": "unified_agent_physical_verification",
                    "status": report.status,
                    "steps_succeeded": report.steps_succeeded,
                    "steps_total": report.steps_total,
                    "verification_summary": report.verification_summary,
                },
            )

        # 1. Model Routing & Capability Detection
        route_res = self.model_router.route_request(
            request.prompt, user_model=request.model, user_provider=request.provider
        )

        model_name = route_res["selected_model"]
        provider_name = route_res["selected_provider"]
        task_category = route_res["task_category"]

        # 2. Check for Deterministic Arithmetic Execution
        if request.use_deterministic_tools and route_res.get("is_deterministic_arithmetic"):
            det_result = self.calculator.extract_and_evaluate(request.prompt)
            if det_result:
                latency_ms = round((time.perf_counter() - t0) * 1000, 2)
                content = det_result["formatted_output"]
                prompt_tokens = int(len(request.prompt.split()) * 1.3)
                completion_tokens = int(len(content.split()) * 1.3)

                log_record = await self.repository.save_request_log(
                    prompt=request.prompt,
                    model_name="deterministic_calculator",
                    provider="local_engine",
                    task_category="Mathematics",
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    latency_ms=latency_ms,
                )

                self.stats_tracker.record_inference(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    ttft_ms=1.0,
                )

                return ChatInferenceResponse(
                    request_id=str(log_record.id),
                    content=content,
                    model="deterministic_calculator",
                    provider="local_engine",
                    task_category="Mathematics",
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                    latency_ms=latency_ms,
                    created_at=cast(Any, log_record.created_at),
                    is_deterministic=True,
                    verification={"valid": True, "method": "deterministic_ast_evaluation"},
                )

        # 2.5 Document Intelligence & Workspace File Grounding
        effective_prompt = request.prompt
        effective_system_prompt = request.system_prompt
        doc_grounding = await self.document_resolver.resolve_document_grounding(request.prompt)

        if doc_grounding:
            if "security_error" in doc_grounding:
                latency_ms = round((time.perf_counter() - t0) * 1000, 2)
                sec_msg = doc_grounding["security_error"]
                log_record = await self.repository.save_request_log(
                    prompt=request.prompt,
                    model_name="workspace_security_guard",
                    provider="local_engine",
                    task_category="File operations",
                    prompt_tokens=int(len(request.prompt.split()) * 1.3),
                    completion_tokens=int(len(sec_msg.split()) * 1.3),
                    latency_ms=latency_ms,
                )
                return ChatInferenceResponse(
                    request_id=str(log_record.id),
                    content=sec_msg,
                    model="workspace_security_guard",
                    provider="local_engine",
                    task_category="File operations",
                    prompt_tokens=int(len(request.prompt.split()) * 1.3),
                    completion_tokens=int(len(sec_msg.split()) * 1.3),
                    total_tokens=int(len(request.prompt.split()) * 1.3) + int(len(sec_msg.split()) * 1.3),
                    latency_ms=latency_ms,
                    created_at=cast(Any, log_record.created_at),
                    is_deterministic=True,
                    verification={"valid": False, "method": "workspace_security_guard", "reason": "access_denied"},
                )

            elif "missing_file_error" in doc_grounding:
                latency_ms = round((time.perf_counter() - t0) * 1000, 2)
                miss_msg = doc_grounding["missing_file_error"]
                log_record = await self.repository.save_request_log(
                    prompt=request.prompt,
                    model_name="document_intelligence",
                    provider="local_engine",
                    task_category="File operations",
                    prompt_tokens=int(len(request.prompt.split()) * 1.3),
                    completion_tokens=int(len(miss_msg.split()) * 1.3),
                    latency_ms=latency_ms,
                )
                return ChatInferenceResponse(
                    request_id=str(log_record.id),
                    content=miss_msg,
                    model="document_intelligence",
                    provider="local_engine",
                    task_category="File operations",
                    prompt_tokens=int(len(request.prompt.split()) * 1.3),
                    completion_tokens=int(len(miss_msg.split()) * 1.3),
                    total_tokens=int(len(request.prompt.split()) * 1.3) + int(len(miss_msg.split()) * 1.3),
                    latency_ms=latency_ms,
                    created_at=cast(Any, log_record.created_at),
                    is_deterministic=True,
                    verification={"valid": False, "method": "workspace_file_check", "reason": "file_not_found"},
                )

            elif "grounded_prefix" in doc_grounding:
                effective_prompt = f"{doc_grounding['grounded_prefix']}\nUser Request: {request.prompt}"
                sys_inst = doc_grounding["system_instruction"]
                effective_system_prompt = f"{effective_system_prompt}\n{sys_inst}" if effective_system_prompt else sys_inst
                task_category = "File operations"

        # 3. GPU Scheduling Allocation
        gpu_res = self.gpu_scheduler.allocate_gpu(vram_required_mb=4096)

        # 4. Provider Backend Execution with Multi-Turn Context
        try:
            dispatch_res = await self.provider_router.dispatch_request(
                provider=provider_name,
                model=model_name,
                prompt=effective_prompt,
                messages=request.messages,
                system_prompt=effective_system_prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
        finally:
            # 5. Release GPU Allocation
            if not gpu_res["fallback_to_cpu"]:
                self.gpu_scheduler.release_gpu(gpu_res["gpu_id"], vram_released_mb=4096)

        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        content = dispatch_res["content"]

        # 6. Response Validation Layer
        verification = self.response_validator.validate_response(
            request.prompt, content, task_category=task_category
        )

        # 7. Persist Log
        log_record = await self.repository.save_request_log(
            prompt=request.prompt,
            model_name=model_name,
            provider=provider_name,
            task_category=task_category,
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
            request_id=str(log_record.id),
            content=content,
            model=model_name,
            provider=provider_name,
            task_category=task_category,
            prompt_tokens=dispatch_res["prompt_tokens"],
            completion_tokens=dispatch_res["completion_tokens"],
            total_tokens=dispatch_res["prompt_tokens"] + dispatch_res["completion_tokens"],
            latency_ms=latency_ms,
            created_at=cast(Any, log_record.created_at),
            is_deterministic=False,
            verification=verification,
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
            is_deterministic_arithmetic=res.get("is_deterministic_arithmetic", False),
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
        self.calculator = DeterministicCalculator()
        self.model_router = ModelRouter()
        self.document_resolver = DocumentContextResolver()
        self.agent_engine = AgentExecutionEngine()
        logger.info("streaming_service_initialized")

    async def stream_chat(
        self,
        prompt: str,
        model: str = "qwen3:8b",
        provider: str = "ollama",
        messages: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        use_deterministic_tools: bool = True,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generates streaming tokens with deterministic shortcut for exact arithmetic and document grounding."""
        # Check Unified Agent Execution Engine for operational tasks and security checks
        task_analysis = self.agent_engine.understand_task(prompt)
        intent = task_analysis["intent"]

        if intent in (
            TaskIntent.SECURITY_VIOLATION,
            TaskIntent.MULTI_STEP_TASK,
            TaskIntent.DESKTOP_OPERATION,
            TaskIntent.FILE_OPERATION,
            TaskIntent.CODE_ANALYSIS,
        ):
            plan = self.agent_engine.create_plan(prompt, task_analysis)
            report = await self.agent_engine.execute_plan(plan)
            lines = report.final_output.split("\n")
            for idx, line in enumerate(lines):
                yield {"token_index": idx, "text": line + "\n", "is_final": False}
                await asyncio.sleep(0.01)
            yield {"token_index": len(lines), "text": "", "is_final": True}
            return

        # Check deterministic arithmetic shortcut
        if use_deterministic_tools:
            route_res = self.model_router.route_request(prompt)
            if route_res.get("is_deterministic_arithmetic"):
                det = self.calculator.extract_and_evaluate(prompt)
                if det:
                    # Stream precomputed deterministic explanation
                    lines = det["formatted_output"].split("\n")
                    idx = 0
                    for line in lines:
                        yield {"token_index": idx, "text": line + "\n", "is_final": False}
                        idx += 1
                        await asyncio.sleep(0.01)
                    yield {"token_index": idx, "text": "", "is_final": True}
                    return

        # Check document grounding & workspace security
        effective_prompt = prompt
        effective_system_prompt = system_prompt
        doc_grounding = await self.document_resolver.resolve_document_grounding(prompt)

        if doc_grounding:
            if "security_error" in doc_grounding:
                yield {"token_index": 0, "text": doc_grounding["security_error"], "is_final": True}
                return
            elif "missing_file_error" in doc_grounding:
                yield {"token_index": 0, "text": doc_grounding["missing_file_error"], "is_final": True}
                return
            elif "grounded_prefix" in doc_grounding:
                effective_prompt = f"{doc_grounding['grounded_prefix']}\nUser Request: {prompt}"
                sys_inst = doc_grounding["system_instruction"]
                effective_system_prompt = f"{effective_system_prompt}\n{sys_inst}" if effective_system_prompt else sys_inst

        async for chunk in self.streaming_engine.stream_tokens(
            effective_prompt,
            model,
            provider,
            messages=messages,
            system_prompt=effective_system_prompt,
            max_tokens=max_tokens,
        ):
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
        return await self.health_checker.run_health_checks_async()
