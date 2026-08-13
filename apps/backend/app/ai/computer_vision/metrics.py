"""Telemetry and performance metrics collector for Computer Vision & Adaptive GUI Intelligence.
"""

import time
from app.ai.computer_vision.models import VisionMetrics


class VisionMetricsTracker:
    """Collects and aggregates computer vision telemetry."""

    def __init__(self) -> None:
        self._screens = 0
        self._elements = 0
        self._ocr_ops = 0
        self._recoveries = 0
        self._total_latency = 0.0

    def record_screen_analyzed(self, elements_found: int, latency_ms: float) -> None:
        """Records telemetry for analyzed desktop screen."""
        self._screens += 1
        self._elements += elements_found
        self._total_latency += latency_ms

    def record_ocr_operation(self) -> None:
        """Increments OCR operations count."""
        self._ocr_ops += 1

    def record_recovery_attempt(self) -> None:
        """Increments automation recovery count."""
        self._recoveries += 1

    def get_metrics(self) -> VisionMetrics:
        """Returns current VisionMetrics snapshot."""
        avg_lat = (self._total_latency / self._screens) if self._screens > 0 else 0.0
        return VisionMetrics(
            screens_analyzed=self._screens,
            elements_located=self._elements,
            ocr_operations=self._ocr_ops,
            recoveries_attempted=self._recoveries,
            average_latency_ms=avg_lat,
            timestamp=time.time(),
        )
