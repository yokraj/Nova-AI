"""Telemetry metrics collector for Real AI Runtime Integration & Local Model Execution Platform.
"""

import time
from app.ai.runtime.models import RuntimeMetrics


class RuntimeMetricsTracker:
    """Collects runtime telemetry metrics and inference timing."""

    def __init__(self) -> None:
        self._total_inferences = 0
        self._local_inferences = 0
        self._cpu_fallbacks = 0
        self._total_latency = 0.0
        self._total_latency_sec = 0.0
        self._total_tokens = 0
        self._tokens_generated = 0

    def record_inference(
        self,
        is_local: bool = True,
        latency_ms: float = 0.0,
        tokens: int = 0,
        cpu_fallback: bool = False,
        model_name: Optional[str] = None,
        duration: Optional[float] = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        success: bool = True,
    ) -> None:
        """Records telemetry metrics for completed inference request."""
        self._total_inferences += 1
        if is_local:
            self._local_inferences += 1
        if cpu_fallback:
            self._cpu_fallbacks += 1
        self._total_latency += latency_ms or (duration * 1000.0 if duration else 0.0)
        self._total_latency_sec += duration if duration is not None else (latency_ms / 1000.0)
        self._total_tokens += tokens or (prompt_tokens + completion_tokens)
        self._tokens_generated += completion_tokens or tokens

    def get_metrics(self) -> RuntimeMetrics:
        """Returns current RuntimeMetrics snapshot."""
        return RuntimeMetrics(
            total_inferences=self._total_inferences,
            local_inferences=self._local_inferences,
            cpu_fallbacks=self._cpu_fallbacks,
            total_latency_ms=self._total_latency,
            total_tokens=self._total_tokens,
            timestamp=time.time(),
        )

    def get_summary(self) -> Dict[str, Any]:
        """Returns telemetry metrics summary dictionary."""
        return {
            "total_inferences": self._total_inferences,
            "local_inferences": self._local_inferences,
            "cpu_fallbacks": self._cpu_fallbacks,
            "total_latency_ms": self._total_latency,
            "total_latency_sec": self._total_latency_sec,
            "total_tokens": self._total_tokens,
            "tokens_generated": self._tokens_generated,
        }






LocalMetricsTracker = RuntimeMetricsTracker

