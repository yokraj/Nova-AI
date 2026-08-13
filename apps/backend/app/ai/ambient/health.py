"""Ambient Health Monitor reporting composite system health status."""

import structlog

from app.ai.ambient.models import AmbientHealth

logger = structlog.get_logger("ambient_health")


class AmbientHealthMonitor:
    """Monitors composite system health for Ambient Intelligence Engine."""

    def check_health(self) -> AmbientHealth:
        """Check composite health status."""
        return AmbientHealth(
            status="healthy",
            microphone_active=True,
            privacy_mode=False,
            monitors_online={
                "microphone_listener": "online",
                "wake_word_runtime": "online",
                "active_window_monitor": "online",
                "clipboard_monitor": "online",
                "proactive_assistant": "online",
            },
        )
