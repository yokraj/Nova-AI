"""Notification Center dispatching workspace alerts, task assignments, and approval holds.
"""

from typing import Any, Dict


class NotificationCenter:
    """Dispatches workspace alerts, task assignments, and human-in-the-loop approval holds."""

    def dispatch_notification(self, recipient_email: str, title: str, message: str) -> Dict[str, Any]:
        """Dispatches notification message to recipient."""
        return {
            "recipient": recipient_email,
            "title": title,
            "message": message,
            "status": "SENT",
        }
