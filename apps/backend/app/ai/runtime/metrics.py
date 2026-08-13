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
        self._total_tokens = 0

    def record_inference(self, is_local: bool, latency_ms: float, tokens: int, cpu_fallback: bool = False) -> None:
        """Records telemetry metrics for completed inference request."""
        self._total_inferences += 1
        if is_local:
            self._local_inferences += 1
        if cpu_fallback:
            self._cpu_fallbacks += 1
        self._total_latency += latency_ms
        self._total_tokens += tokens

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
