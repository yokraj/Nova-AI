"""Telemetry and performance metrics collector for AI Model Integration Platform.
"""

import time
from app.ai.models.models import ModelMetrics


class ModelMetricsTracker:
    """Collects and aggregates model routing and inference metrics."""

    def __init__(self) -> None:
        self._total_requests = 0
        self._local_inferences = 0
        self._remote_inferences = 0
        self._fallbacks = 0
        self._total_latency = 0.0
        self._total_tokens = 0

    def record_routing_request(self, is_local: bool, latency_ms: float, tokens: int, fallback: bool = False) -> None:
        """Records telemetry for a model routing request."""
        self._total_requests += 1
        if is_local:
            self._local_inferences += 1
        else:
            self._remote_inferences += 1
        if fallback:
            self._fallbacks += 1
        self._total_latency += latency_ms
        self._total_tokens += tokens

    def get_metrics(self) -> ModelMetrics:
        """Returns current ModelMetrics snapshot."""
        avg_lat = (self._total_latency / self._total_requests) if self._total_requests > 0 else 0.0
        return ModelMetrics(
            total_routing_requests=self._total_requests,
            local_inferences=self._local_inferences,
            remote_inferences=self._remote_inferences,
            fallbacks_triggered=self._fallbacks,
            average_latency_ms=avg_lat,
            total_tokens_processed=self._total_tokens,
            timestamp=time.time(),
        )
