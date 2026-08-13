"""Automation Metrics Tracker recording execution telemetry metrics."""

from typing import Dict, Any
import structlog

from app.ai.automation.models import AutomationMetrics

logger = structlog.get_logger("automation_metrics")


class AutomationMetricsTracker:
    """Tracks telemetry metrics for desktop and browser automation."""

    def __init__(self) -> None:
        self._total = 0
        self._successes = 0
        self._failures = 0
        self._total_duration = 0.0
        self._desktop_count = 0
        self._browser_count = 0
        self._ocr_count = 0
        self._form_count = 0

    def record_action(self, category: str) -> None:
        """Increment category counter."""
        self._total += 1
        if category == "desktop":
            self._desktop_count += 1
        elif category == "browser":
            self._browser_count += 1
        elif category == "ocr":
            self._ocr_count += 1
        elif category == "form":
            self._form_count += 1

    def record_success(self, duration_seconds: float) -> None:
        """Record successful automation."""
        self._successes += 1
        self._total_duration += duration_seconds

    def record_failure(self) -> None:
        """Record failed automation."""
        self._failures += 1

    def get_metrics(self) -> AutomationMetrics:
        """Get metrics snapshot."""
        rate = (self._successes / self._total * 100.0) if self._total > 0 else 100.0
        avg_dur = (self._total_duration / self._successes) if self._successes > 0 else 0.0
        return AutomationMetrics(
            total_automations=self._total,
            successful_automations=self._successes,
            failed_automations=self._failures,
            success_rate=rate,
            average_duration_seconds=avg_dur,
            desktop_actions_count=self._desktop_count,
            browser_actions_count=self._browser_count,
            ocr_extractions_count=self._ocr_count,
            form_fills_count=self._form_count,
        )
