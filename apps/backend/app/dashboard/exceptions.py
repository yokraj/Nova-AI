"""Dashboard Exceptions Module.

Defines custom exception classes for dashboard domain errors, state violations,
missing records, and infrastructure integration faults.
"""


class DashboardException(Exception):
    """Base exception class for all enterprise dashboard domain errors."""

    def __init__(self, message: str = "Dashboard service error occurred.") -> None:
        self.message = message
        super().__init__(self.message)


class DashboardConfigError(DashboardException):
    """Raised when dashboard configuration parameters are invalid or missing."""

    pass


class DashboardCacheError(DashboardException):
    """Raised when dashboard cache read/write operations encounter failure."""

    pass


class DashboardSubscriptionError(DashboardException):
    """Raised when event subscription or WebSocket channel registration fails."""

    pass


# Specific Entity Not Found Exceptions


class DashboardNotFoundError(DashboardException):
    """Raised when requested dashboard snapshot or resource is not found."""

    def __init__(self, identifier: str = "") -> None:
        msg = f"Dashboard snapshot '{identifier}' not found." if identifier else "Dashboard snapshot not found."
        super().__init__(msg)


class NotificationNotFoundError(DashboardException):
    """Raised when requested dashboard notification is not found."""

    def __init__(self, identifier: str = "") -> None:
        msg = f"Notification '{identifier}' not found." if identifier else "Notification not found."
        super().__init__(msg)


class MetricNotFoundError(DashboardException):
    """Raised when requested metric record is not found."""

    def __init__(self, identifier: str = "") -> None:
        msg = f"Metric record '{identifier}' not found." if identifier else "Metric record not found."
        super().__init__(msg)


class HealthRecordNotFoundError(DashboardException):
    """Raised when requested health diagnostic record is not found."""

    def __init__(self, identifier: str = "") -> None:
        msg = f"Health record '{identifier}' not found." if identifier else "Health record not found."
        super().__init__(msg)


class ConfigurationNotFoundError(DashboardException):
    """Raised when requested configuration setting is not found."""

    def __init__(self, identifier: str = "") -> None:
        msg = f"Configuration record '{identifier}' not found." if identifier else "Configuration record not found."
        super().__init__(msg)


class EventNotFoundError(DashboardException):
    """Raised when requested dashboard event is not found."""

    def __init__(self, identifier: str = "") -> None:
        msg = f"Dashboard event '{identifier}' not found." if identifier else "Dashboard event not found."
        super().__init__(msg)
