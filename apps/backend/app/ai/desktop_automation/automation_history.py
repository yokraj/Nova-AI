"""Automation History recording executed actions, failures, recoveries, and user confirmations.
"""

from typing import Any, Dict, List
from app.ai.desktop_automation.models import AutomationResult


class AutomationHistory:
    """Stores persistent execution history logs, recovery outcomes, and performance metrics."""

    def __init__(self) -> None:
        self._history: List[AutomationResult] = []

    def record_result(self, result: AutomationResult) -> None:
        """Records automation step result."""
        self._history.append(result)

    def get_history(self) -> List[AutomationResult]:
        """Returns execution history log."""
        return list(self._history)
