"""Telemetry metrics tracker for Universal Desktop, Browser & OS Automation Engine.
"""

import time
from app.ai.desktop_automation.models import DesktopMetrics


class DesktopAutomationMetricsTracker:
    """Collects total, verified, recovered, and failed action execution metrics."""

    def __init__(self) -> None:
        self._total_actions = 0
        self._verified_actions = 0
        self._recovered_actions = 0
        self._failed_actions = 0

    def record_action_executed(self, verified: bool = True, recovered: bool = False) -> None:
        """Records executed action."""
        self._total_actions += 1
        if verified:
            self._verified_actions += 1
        if recovered:
            self._recovered_actions += 1

    def record_action_failed(self) -> None:
        """Records action failure."""
        self._total_actions += 1
        self._failed_actions += 1

    def get_metrics(self) -> DesktopMetrics:
        """Returns DesktopMetrics telemetry snapshot."""
        return DesktopMetrics(
            total_actions=self._total_actions,
            verified_actions=self._verified_actions,
            recovered_actions=self._recovered_actions,
            failed_actions=self._failed_actions,
            timestamp=time.time(),
        )
