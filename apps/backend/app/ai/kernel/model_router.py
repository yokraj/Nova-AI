"""Native Local-First Model Router for Nova-AI's Cognitive Kernel (Phase 10E).

Provides workload-driven local model selection, context budget matching, structured output
enforcement, health monitoring, deterministic local fallback chains, zero-cost enforcement,
and routing telemetry recording.
"""

from dataclasses import dataclass, field
from enum import Enum
import json
import threading
import time
from typing import Any, Dict, List, Optional, Tuple
import urllib.request
import uuid

import structlog

logger = structlog.get_logger("model_router")


class CognitiveWorkloadType(str, Enum):
    """Classifies cognitive tasks for specialized local model routing."""

    INTENT_UNDERSTANDING = "intent_understanding"
    TASK_DECOMPOSITION = "task_decomposition"
    PLANNING = "planning"
    TOOL_SELECTION = "tool_selection"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    VERIFICATION_CRITIQUE = "verification_critique"
    RECOVERY_REPLANNING = "recovery_replanning"
    CONTEXT_COMPRESSION = "context_compression"


@dataclass
class ModelProfile:
    """Canonical description of a local AI model and its capability profile."""

    model_id: str
    name: str
    provider_type: str = "ollama"
    context_window: int = 40960
    reasoning_score: float = 0.85
    code_score: float = 0.85
    tool_use_score: float = 0.85
    structured_output_score: float = 0.85
    latency_tier: str = "medium"  # fast, medium, slow
    vram_mb: int = 5120
    ram_mb: int = 8192
    is_healthy: bool = True
    is_local: bool = True
    priority: int = 10
    custom_registered: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "name": self.name,
            "provider_type": self.provider_type,
            "context_window": self.context_window,
            "reasoning_score": self.reasoning_score,
            "code_score": self.code_score,
            "tool_use_score": self.tool_use_score,
            "structured_output_score": self.structured_output_score,
            "latency_tier": self.latency_tier,
            "vram_mb": self.vram_mb,
            "ram_mb": self.ram_mb,
            "is_healthy": self.is_healthy,
            "is_local": self.is_local,
            "priority": self.priority,
        }


@dataclass
class RoutingConstraints:
    """Routing constraints passed alongside cognitive workload requests."""

    min_context_tokens: int = 0
    require_tools: bool = False
    require_structured_output: bool = False
    max_latency_budget_ms: Optional[float] = None
    preferred_model_id: Optional[str] = None
    max_vram_mb: Optional[int] = None
    allow_cloud_fallback: bool = False  # 100% Local-first default


@dataclass
class RoutingDecision:
    """Telemetry payload recording model selection rationale and execution metrics."""

    decision_id: str = field(default_factory=lambda: f"dec_{uuid.uuid4().hex[:8]}")
    workload_type: CognitiveWorkloadType = CognitiveWorkloadType.REASONING
    selected_model_id: str = "qwen3:8b"
    provider_type: str = "ollama"
    routing_reason: str = "Default local reasoning model selected"
    fallback_used: bool = False
    fallback_reason: Optional[str] = None
    confidence_score: float = 0.95
    latency_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)
    success: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "workload_type": self.workload_type.value if isinstance(self.workload_type, Enum) else self.workload_type,
            "selected_model_id": self.selected_model_id,
            "provider_type": self.provider_type,
            "routing_reason": self.routing_reason,
            "fallback_used": self.fallback_used,
            "fallback_reason": self.fallback_reason,
            "confidence_score": self.confidence_score,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp,
            "success": self.success,
        }


class LocalModelRouter:
    """Workload-driven Local Model Router orchestrating Ollama and local model selection."""

    _instance: Optional["LocalModelRouter"] = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "LocalModelRouter":
        """Singleton accessor."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def __init__(self, ollama_endpoint: str = "http://localhost:11434") -> None:
        self.ollama_endpoint = ollama_endpoint
        self.registered_models: Dict[str, ModelProfile] = {}
        self.telemetry_history: List[RoutingDecision] = []
        self._seed_default_profiles()

    def _seed_default_profiles(self) -> None:
        """Seeds default known local model profiles."""
        defaults = [
            ModelProfile(
                model_id="qwen3:8b",
                name="Qwen 3 8B Instruct Reasoning",
                provider_type="ollama",
                context_window=40960,
                reasoning_score=0.92,
                code_score=0.90,
                tool_use_score=0.92,
                structured_output_score=0.90,
                latency_tier="medium",
                vram_mb=5120,
                is_local=True,
                priority=10,
            ),
            ModelProfile(
                model_id="qwen2.5-coder:7b",
                name="Qwen 2.5 Coder 7B",
                provider_type="ollama",
                context_window=32768,
                reasoning_score=0.82,
                code_score=0.95,
                tool_use_score=0.88,
                structured_output_score=0.92,
                latency_tier="medium",
                vram_mb=4600,
                is_local=True,
                priority=9,
            ),
            ModelProfile(
                model_id="deepseek-r1:8b",
                name="DeepSeek R1 Distill 8B",
                provider_type="ollama",
                context_window=32768,
                reasoning_score=0.96,
                code_score=0.88,
                tool_use_score=0.82,
                structured_output_score=0.85,
                latency_tier="slow",
                vram_mb=5200,
                is_local=True,
                priority=9,
            ),
            ModelProfile(
                model_id="qwen2.5-vl:7b",
                name="Qwen 2.5 VL 7B Vision",
                provider_type="ollama",
                context_window=16384,
                reasoning_score=0.80,
                code_score=0.75,
                tool_use_score=0.80,
                structured_output_score=0.80,
                latency_tier="medium",
                vram_mb=5120,
                is_local=True,
                priority=8,
            ),
            ModelProfile(
                model_id="bge-small-en-v1.5",
                name="BGE Small English Embeddings",
                provider_type="bge_embedding",
                context_window=512,
                reasoning_score=0.0,
                code_score=0.0,
                tool_use_score=0.0,
                structured_output_score=0.0,
                latency_tier="fast",
                vram_mb=512,
                is_local=True,
                priority=10,
            ),
        ]
        for p in defaults:
            self.registered_models[p.model_id] = p

    def register_model(self, profile: ModelProfile) -> None:
        """Registers or updates a local model profile."""
        profile.custom_registered = True
        self.registered_models[profile.model_id] = profile
        logger.debug("Registered model profile", model_id=profile.model_id)

    def check_ollama_server_health(self) -> Tuple[bool, List[str]]:
        """Pings local Ollama API server and returns list of installed models."""
        try:
            url = f"{self.ollama_endpoint}/api/tags"
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    models = [m.get("name", "") for m in data.get("models", []) if m.get("name")]
                    return True, models
        except Exception as e:
            logger.warning("Ollama server health check failed", endpoint=self.ollama_endpoint, error=str(e))
        return False, []

    def refresh_available_models(self) -> List[str]:
        """Auto-discovers installed Ollama models and updates health statuses."""
        is_online, installed = self.check_ollama_server_health()
        for mid, profile in self.registered_models.items():
            if profile.provider_type == "ollama":
                if not is_online:
                    if not profile.custom_registered:
                        profile.is_healthy = False
                elif installed:
                    is_inst = any(
                        mid == inst or mid.split(":")[0] == inst.split(":")[0]
                        for inst in installed
                    )
                    if not is_inst and not profile.custom_registered:
                        profile.is_healthy = False
        return installed

    def _calculate_workload_suitability(
        self, profile: ModelProfile, workload: CognitiveWorkloadType, constraints: RoutingConstraints
    ) -> float:
        """Calculates suitability score (0.0 to 1.0) for a model against a workload class."""
        if not profile.is_healthy:
            return 0.0

        if constraints.min_context_tokens > profile.context_window:
            return 0.0

        if constraints.require_tools and profile.tool_use_score < 0.5:
            return 0.0

        if constraints.require_structured_output and profile.structured_output_score < 0.5:
            return 0.0

        if constraints.max_vram_mb and profile.vram_mb > constraints.max_vram_mb:
            return 0.0

        if workload == CognitiveWorkloadType.CODE_GENERATION:
            base = profile.code_score
        elif workload in [CognitiveWorkloadType.REASONING, CognitiveWorkloadType.PLANNING, CognitiveWorkloadType.TASK_DECOMPOSITION, CognitiveWorkloadType.RECOVERY_REPLANNING]:
            base = profile.reasoning_score
        elif workload == CognitiveWorkloadType.TOOL_SELECTION:
            base = (profile.tool_use_score * 0.6) + (profile.structured_output_score * 0.4)
        elif workload in [CognitiveWorkloadType.INTENT_UNDERSTANDING, CognitiveWorkloadType.CONTEXT_COMPRESSION]:
            base = 0.8 + (0.2 if profile.latency_tier == "fast" else 0.0)
        else:
            base = profile.reasoning_score

        priority_bonus = min(0.05, profile.priority * 0.005)
        return min(1.0, base + priority_bonus)

    async def route_workload(
        self,
        workload_type: CognitiveWorkloadType,
        constraints: Optional[RoutingConstraints] = None,
    ) -> RoutingDecision:
        """Routes a cognitive workload request to the optimal local model."""
        start_t = time.time()
        c = constraints or RoutingConstraints()

        self.refresh_available_models()

        selected_model: Optional[ModelProfile] = None
        fallback_used = False
        fallback_reason = None
        reason = ""

        # 1. Check preferred model override
        if c.preferred_model_id:
            if c.preferred_model_id in self.registered_models:
                pref = self.registered_models[c.preferred_model_id]
                if pref.is_healthy:
                    selected_model = pref
                    reason = f"Preferred model override '{c.preferred_model_id}' satisfied constraints"
                else:
                    fallback_used = True
                    fallback_reason = f"Preferred model '{c.preferred_model_id}' is unhealthy"
            else:
                fallback_used = True
                fallback_reason = f"Preferred model '{c.preferred_model_id}' is not registered"

        # 2. Workload suitability ranking
        if not selected_model:
            candidates: List[Tuple[ModelProfile, float]] = []
            for profile in self.registered_models.values():
                if profile.provider_type != "ollama":
                    continue
                score = self._calculate_workload_suitability(profile, workload_type, c)
                if score > 0.0:
                    candidates.append((profile, score))

            candidates.sort(key=lambda x: x[1], reverse=True)

            if candidates:
                selected_model = candidates[0][0]
                if not fallback_used:
                    reason = f"Optimal local model selected for workload {workload_type.value} (score={candidates[0][1]:.2f})"

        # 3. Deterministic Local Fallback Chain
        if not selected_model:
            fallback_used = True
            if not fallback_reason:
                fallback_reason = f"No specialized model met strict constraints for {workload_type.value}. Triggering deterministic fallback."

            healthy_ollama = [m for m in self.registered_models.values() if m.provider_type == "ollama" and m.is_healthy]
            if healthy_ollama:
                healthy_ollama.sort(key=lambda m: m.priority, reverse=True)
                selected_model = healthy_ollama[0]
                reason = f"Fallback to highest priority healthy local model '{selected_model.model_id}'"
            else:
                selected_model = self.registered_models.get("qwen3:8b") or list(self.registered_models.values())[0]
                reason = f"Emergency fallback to registered profile '{selected_model.model_id}'"

        elapsed_ms = round((time.time() - start_t) * 1000.0, 2)

        decision = RoutingDecision(
            workload_type=workload_type,
            selected_model_id=selected_model.model_id,
            provider_type=selected_model.provider_type,
            routing_reason=reason,
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
            confidence_score=0.96 if not fallback_used else 0.75,
            latency_ms=elapsed_ms,
            success=True,
        )

        self.telemetry_history.append(decision)
        logger.info(
            "Model routing decision completed",
            workload=workload_type.value,
            selected=selected_model.model_id,
            fallback=fallback_used,
            latency_ms=elapsed_ms,
        )
        return decision

    def route(
        self,
        workload_type: CognitiveWorkloadType,
        constraints: Optional[RoutingConstraints] = None,
        prompt_sample: str = "",
    ) -> RoutingDecision:
        """Synchronous routing convenience wrapper."""
        import asyncio
        try:
            return asyncio.run(self.route_workload(workload_type, constraints))
        except RuntimeError:
            # Handle if already running in an event loop
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(lambda: asyncio.run(self.route_workload(workload_type, constraints))).result()

    def get_telemetry_history(self) -> List[RoutingDecision]:
        """Returns recorded model routing decision telemetry history."""
        return list(self.telemetry_history)

    def clear_telemetry_history(self) -> None:
        """Clears telemetry history."""
        self.telemetry_history.clear()
