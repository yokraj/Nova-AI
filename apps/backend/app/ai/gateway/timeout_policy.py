"""Timeout policy managing execution runtime boundaries for requests.
"""


class TimeoutPolicy:
    """Configures timeout thresholds constraints for API queries."""

    def __init__(self, timeout_seconds: float = 30.0) -> None:
        """Initializes TimeoutPolicy.

        Args:
            timeout_seconds: Timeout limit in seconds.
        """
        self.timeout_seconds = timeout_seconds
