"""Proactive Voice Notification Engine.
"""

from typing import List
from app.ai.os_runtime.interfaces import IVoiceNotificationEngine
from app.ai.os_runtime.models import ProactiveVoiceNotification


class VoiceNotificationEngine(IVoiceNotificationEngine):
    """Speaks proactive notifications for completed missions, failed builds, docker status, meetings, low battery."""

    def __init__(self) -> None:
        self._history: List[ProactiveVoiceNotification] = []

    async def notify_voice(self, title: str, message: str) -> ProactiveVoiceNotification:
        """Dispatches proactive voice notification alert."""
        notif = ProactiveVoiceNotification(
            title=title,
            message=message,
            category="alert",
            spoken=True,
        )
        self._history.append(notif)
        return notif

    def get_notification_history(self) -> List[ProactiveVoiceNotification]:
        return self._history
