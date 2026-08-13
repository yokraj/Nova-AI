"""Metrics collector for RAG database searches.
"""

import structlog
from typing import Optional
from app.agent_sdk.observability.metrics import MetricsCollector

logger = structlog.get_logger(__name__)

class MemoryMetricsTracker:
    """Publishes RAG embedding and retrieval stats to the Observability System."""

    def __init__(self, collector: Optional[MetricsCollector] = None) -> None:
        self.collector = collector or MetricsCollector()
        self.memory_count = 0
        self.retrieval_latency_ms = 0.0
        self.embedding_time_ms = 0.0

    def record_retrieval(self, latency_ms: float) -> None:
        """Saves search duration telemetry metrics."""
        self.retrieval_latency_ms += latency_ms
        self.collector.record_execution(latency_ms / 1000.0, True)
        
        logger.info("rag_memory_retrieval_metrics", latency_ms=latency_ms)

    def record_embedding(self, duration_ms: float) -> None:
        """Saves embedding generation duration metrics."""
        self.embedding_time_ms += duration_ms
        logger.info("rag_memory_embedding_metrics", duration_ms=duration_ms)
