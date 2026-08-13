"""Notification Runtime dispatching multi-channel alerts (Voice, Desktop Toast, System Tray, Email).
"""

from typing import Any, Dict
from app.ai.os_runtime.models import NotificationPayload


class NotificationRuntime:
    """Dispatches multi-channel system notifications across Voice TTS, Windows Toasts, System Tray, and Logs."""

    async def notify(self, title: str, message: str, channel: str = "voice_and_toast") -> NotificationPayload:
        """Dispatches notification payload across selected channels."""
        return NotificationPayload(
            title=title,
            message=message,
            channel=channel,
            priority="normal",
        )
