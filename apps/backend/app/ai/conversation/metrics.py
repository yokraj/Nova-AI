"""Telemetry metrics collector for Human-Like Conversation & EI Engine.
"""

import time
from app.ai.conversation.models import ConversationMetrics


class ConversationMetricsTracker:
    """Collects conversation metrics, turns, emotion detections, and latency."""

    def __init__(self) -> None:
        self._total_conversations = 0
        self._total_turns = 0
        self._emotions_detected = 0
        self._interruptions_handled = 0
        self._total_latency = 0.0

    def record_turn(self, emotion_detected: bool, latency_ms: float) -> None:
        """Records turn execution metrics."""
        self._total_turns += 1
        if emotion_detected:
            self._emotions_detected += 1
        self._total_latency += latency_ms

    def record_conversation(self) -> None:
        """Records new conversation session."""
        self._total_conversations += 1

    def record_interruption(self) -> None:
        """Records human interruption event."""
        self._interruptions_handled += 1

    def get_metrics(self) -> ConversationMetrics:
        """Returns current ConversationMetrics snapshot."""
        avg_lat = (self._total_latency / self._total_turns) if self._total_turns > 0 else 0.0
        return ConversationMetrics(
            total_conversations=self._total_conversations,
            total_turns=self._total_turns,
            emotions_detected=self._emotions_detected,
            interruptions_handled=self._interruptions_handled,
            avg_latency_ms=avg_lat,
            timestamp=time.time(),
        )
