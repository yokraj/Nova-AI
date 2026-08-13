"""Collaboration metrics collector and summarizer.
"""

from typing import Dict, Any, List

class CollaborationMetricsTracker:
    """Tracks latency metrics, message counters, handoffs completed, and conflict rates."""

    def __init__(self) -> None:
        self.latency_ms: List[float] = []
        self.message_count: int = 0
        self.handoff_count: int = 0
        self.consensus_count: int = 0
        self.conflict_count: int = 0
        self.success_count: int = 0
        self.failure_count: int = 0

    def record_latency(self, duration: float) -> None:
        """Saves duration log in milliseconds."""
        self.latency_ms.append(duration)

    def record_message(self) -> None:
        """Increments message counter."""
        self.message_count += 1

    def record_handoff(self) -> None:
        """Increments handoffs counter."""
        self.handoff_count += 1

    def record_consensus(self) -> None:
        """Increments consensus checks counter."""
        self.consensus_count += 1

    def record_conflict(self) -> None:
        """Increments conflict counter."""
        self.conflict_count += 1

    def record_outcome(self, success: bool) -> None:
        """Records final result outcome status."""
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

    def dump_summary(self) -> Dict[str, Any]:
        """Dumps metrics analytics dictionary summary."""
        avg_lat = sum(self.latency_ms) / len(self.latency_ms) if self.latency_ms else 0.0
        return {
            "avg_latency_ms": avg_lat,
            "messages_exchanged": self.message_count,
            "handoff_count": self.handoff_count,
            "consensus_count": self.consensus_count,
            "conflict_count": self.conflict_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count
        }
