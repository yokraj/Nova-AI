"""Notification Engine Exception Hierarchy Module.

Defines custom exception classes for rule matching, queueing errors, delivery failures,
priority calculations, deduplication, and retention cleanup issues.
"""


class NotificationEngineError(Exception):
    """Base exception class for all Notification Engine failures."""

    def __init__(self, message: str = "Notification engine error occurred.") -> None:
        self.message = message
        super().__init__(self.message)


class NotificationRuleError(NotificationEngineError):
    """Raised when evaluating or registering a notification rule fails."""

    def __init__(self, rule_name: str, detail: str) -> None:
        super().__init__(f"Rule error in '{rule_name}': {detail}")


class NotificationDeliveryError(NotificationEngineError):
    """Raised when delivering a notification over WebSocket or channel fails."""

    def __init__(self, notification_id: str, detail: str) -> None:
        super().__init__(f"Delivery failed for notification '{notification_id}': {detail}")


class NotificationQueueError(NotificationEngineError):
    """Raised when priority queue push or pop operations fail."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Notification queue error: {detail}")


class DuplicateNotificationError(NotificationEngineError):
    """Raised when a duplicate notification is detected and rejected."""

    def __init__(self, fingerprint: str) -> None:
        super().__init__(f"Duplicate notification rejected (hash: '{fingerprint}').")


class PriorityCalculationError(NotificationEngineError):
    """Raised when priority calculation fails for an event payload."""

    def __init__(self, event_type: str, detail: str) -> None:
        super().__init__(f"Priority calculation failed for '{event_type}': {detail}")


class CleanupError(NotificationEngineError):
    """Raised when retention cleanup or purging encounters failure."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Notification cleanup error: {detail}")


class AnalyticsError(NotificationEngineError):
    """Raised when analytics tracking or summary generation fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(f"Notification analytics error: {detail}")
