"""Telemetry and performance metrics collector for AI OS Kernel.
"""

import time
from typing import Dict
from app.ai.kernel.models import KernelMetrics


class KernelMetricsTracker:
    """Collects and aggregates kernel execution telemetry."""

    def __init__(self) -> None:
        self._total = 0
        self._success = 0
        self._failure = 0
        self._total_latency = 0.0
        self._subsystems: Dict[str, int] = {}
        self._voice_responses = 0
        self._security_challenges = 0

    def record_intent(self, latency_ms: float, success: bool = True, voice: bool = False, challenge: bool = False) -> None:
        """Records telemetry for processed intent."""
        self._total += 1
        if success:
            self._success += 1
        else:
            self._failure += 1

        self._total_latency += latency_ms
        if voice:
            self._voice_responses += 1
        if challenge:
            self._security_challenges += 1

    def record_subsystem_call(self, subsystem: str) -> None:
        """Increments invocation count for target subsystem."""
        self._subsystems[subsystem] = self._subsystems.get(subsystem, 0) + 1

    def get_metrics(self) -> KernelMetrics:
        """Returns current KernelMetrics snapshot."""
        avg_lat = (self._total_latency / self._total) if self._total > 0 else 0.0
        return KernelMetrics(
            total_intents_processed=self._total,
            success_count=self._success,
            failure_count=self._failure,
            average_latency_ms=avg_lat,
            subsystem_invocations=self._subsystems,
            voice_responses_count=self._voice_responses,
            security_challenges_count=self._security_challenges,
            timestamp=time.time(),
        )
