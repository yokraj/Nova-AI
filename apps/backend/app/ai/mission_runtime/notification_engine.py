"""Notification Engine dispatching multi-channel alerts (Voice, Desktop, Email, Logs).
"""

from typing import Any, Dict, List
from app.ai.mission_runtime.interfaces import INotificationEngine
from app.ai.mission_runtime.models import MissionPriority, NotificationMessage


class NotificationEngine(INotificationEngine):
    """Notification Engine managing multi-channel user alerts."""

    def __init__(self) -> None:
        self._sent_messages: List[NotificationMessage] = []

    async def send_notification(self, title: str, body: str, channel: str = "voice") -> NotificationMessage:
        """Dispatches an alert message across target notification channel.

        Args:
            title: Notification header.
            body: Alert details text.
            channel: Target channel (voice, desktop, email, log).

        Returns:
            NotificationMessage model instance.
        """
        msg = NotificationMessage(
            channel=channel,
            title=title,
            body=body,
            priority=MissionPriority.NORMAL,
        )
        self._sent_messages.append(msg)
        return msg

    def get_history(self) -> List[NotificationMessage]:
        """Returns history of sent notifications."""
        return self._sent_messages
