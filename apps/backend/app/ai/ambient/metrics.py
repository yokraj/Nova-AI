"""Ambient Metrics Tracker recording telemetry metrics."""

import structlog

from app.ai.ambient.models import AmbientMetrics

logger = structlog.get_logger("ambient_metrics")


class AmbientMetricsTracker:
    """Tracks telemetry metrics for Ambient Intelligence Engine."""

    def __init__(self) -> None:
        self._frames_processed = 0
        self._wake_words = 0
        self._conversations = 0
        self._suggestions = 0
        self._missions = 0
        self._privacy_toggles = 0

    def record_frame(self) -> None:
        self._frames_processed += 1

    def record_wake_word(self) -> None:
        self._wake_words += 1

    def record_conversation(self) -> None:
        self._conversations += 1

    def record_suggestion(self) -> None:
        self._suggestions += 1

    def record_mission(self) -> None:
        self._missions += 1

    def record_privacy_toggle(self) -> None:
        self._privacy_toggles += 1

    def get_metrics(self) -> AmbientMetrics:
        """Get metrics snapshot."""
        return AmbientMetrics(
            audio_frames_processed=self._frames_processed,
            wake_words_detected=self._wake_words,
            conversations_handled=self._conversations,
            proactive_suggestions_issued=self._suggestions,
            missions_auto_created=self._missions,
            privacy_toggles_count=self._privacy_toggles,
        )
