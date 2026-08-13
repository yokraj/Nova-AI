"""Metrics tracker for speech recognition and synthesis latency.
"""

import structlog
from typing import Optional
from app.agent_sdk.observability.metrics import MetricsCollector

logger = structlog.get_logger(__name__)

class VoiceMetricsTracker:
    """Tracks latency metrics for Voice pipeline completions."""

    def __init__(self, collector: Optional[MetricsCollector] = None) -> None:
        self.collector = collector or MetricsCollector()
        self.transcription_time_ms = 0.0
        self.synthesis_time_ms = 0.0

    def record_transcription(self, duration_ms: float) -> None:
        """Saves transcription duration parameters."""
        self.transcription_time_ms += duration_ms
        self.collector.record_execution(duration_ms / 1000.0, True)
        logger.info("voice_transcription_metrics", duration_ms=duration_ms)

    def record_synthesis(self, duration_ms: float) -> None:
        """Saves synthesis duration parameters."""
        self.synthesis_time_ms += duration_ms
        self.collector.record_execution(duration_ms / 1000.0, True)
        logger.info("voice_synthesis_metrics", duration_ms=duration_ms)
