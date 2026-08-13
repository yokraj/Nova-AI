"""Metrics tracking for routing pipeline choices and latencies.
"""

import structlog
from typing import Dict, Any, Optional
from app.agent_sdk.observability.metrics import MetricsCollector

logger = structlog.get_logger(__name__)

class RouterMetricsTracker:
    """Publishes routing selection statistics to Observability SDK."""

    def __init__(self, collector: Optional[MetricsCollector] = None) -> None:
        self.collector = collector or MetricsCollector()
        self.decisions_count = 0
        self.fallback_count = 0
        self.total_latency_ms = 0.0

    def record_decision(self, latency_ms: float, fallback_triggered: bool) -> None:
        """Saves telemetry updates for a model routing cycle."""
        self.decisions_count += 1
        self.total_latency_ms += latency_ms
        if fallback_triggered:
            self.fallback_count += 1

        # Sync with Observability MetricsCollector
        self.collector.record_execution(latency_ms / 1000.0, True)

        logger.info(
            "model_router_decision_telemetry",
            latency_ms=latency_ms,
            fallback_triggered=fallback_triggered
        )
