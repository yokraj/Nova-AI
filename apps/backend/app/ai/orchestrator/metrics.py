"""Telemetry metrics tracker for Universal AI Orchestrator.
"""

import time
from typing import Dict


class OrchestratorMetricsTracker:
    """Collects runtime telemetry stats (inferences, throughput, latency, routing decisions, cache hits)."""

    def __init__(self) -> None:
        self.total_inferences: int = 0
        self.total_tokens_processed: int = 0
        self.total_cache_hits: int = 0
        self.total_routing_decisions: int = 0
        self.total_fallback_triggers: int = 0
        self.start_time: float = time.time()
        self.latencies_sum_ms: float = 0.0

    def record_inference(self, tokens: int = 50, latency_ms: float = 100.0, cached: bool = False, fallback: bool = False) -> None:
        self.total_inferences += 1
        self.total_tokens_processed += tokens
        self.latencies_sum_ms += latency_ms
        if cached:
            self.total_cache_hits += 1
        if fallback:
            self.total_fallback_triggers += 1

    def record_routing_decision(self) -> None:
        self.total_routing_decisions += 1

    def get_metrics_snapshot(self) -> Dict[str, Any]:
        avg_latency = (self.latencies_sum_ms / self.total_inferences) if self.total_inferences > 0 else 0.0
        uptime = time.time() - self.start_time
        return {
            "total_inferences": self.total_inferences,
            "total_tokens_processed": self.total_tokens_processed,
            "total_cache_hits": self.total_cache_hits,
            "total_routing_decisions": self.total_routing_decisions,
            "total_fallback_triggers": self.total_fallback_triggers,
            "average_latency_ms": round(avg_latency, 2),
            "uptime_seconds": round(uptime, 2),
            "tokens_per_second": round(self.total_tokens_processed / max(1.0, uptime), 2),
        }
