"""CancellationToken signalling task cancellation flags.
"""

from app.agent_sdk.execution.exceptions import CancelledExecutionError


class CancellationToken:
    """Token to signal cancellation across async execution scopes."""

    def __init__(self) -> None:
        """Initializes CancellationToken."""
        self._cancelled: bool = False

    def cancel(self) -> None:
        """Flags token as cancelled."""
        self._cancelled = True

    def is_cancelled(self) -> bool:
        """Checks if cancellation has been flagged.

        Returns:
            True if cancelled.
        """
        return self._cancelled

    def throw_if_cancelled(self) -> None:
        """Throws CancelledExecutionError if cancellation was flagged.

        Raises:
            CancelledExecutionError: If cancellation token is active.
        """
        if self._cancelled:
            raise CancelledExecutionError("Execution cancelled by user or coordinator.")
