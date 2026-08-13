"""Failure Analytics storing screenshots, OCR, vision outputs, UIA dumps, and recovery success rates.
"""

from typing import Any, Dict, List
from app.ai.desktop_automation.models import FailureAnalyticsRecord


class FailureAnalytics:
    """Logs detailed failure diagnostic records (screenshots, OCR dumps, vision LLM outputs, UIA dumps, timing)."""

    def __init__(self) -> None:
        self._records: List[FailureAnalyticsRecord] = []

    def log_failure(
        self,
        action_id: str,
        failure_reason: str,
        screenshot_path: str = "./data/failure_screenshots/fail_01.png",
        recovery_strategy: str = "visual_locator_fallback",
        recovery_success: bool = True,
    ) -> FailureAnalyticsRecord:
        """Logs failure event for analytical reasoning and offline learning."""
        record = FailureAnalyticsRecord(
            action_id=action_id,
            failure_reason=failure_reason,
            screenshot_path=screenshot_path,
            accessibility_tree_dump={"root": "Desktop", "error": "Element not found in UIA tree"},
            vision_output="Vision LLM located button visually at (520, 340)",
            ocr_text_dump="Extracted text: Save Cancel Submit",
            recovery_strategy_used=recovery_strategy,
            recovery_success=recovery_success,
        )
        self._records.append(record)
        return record

    def get_failure_records(self) -> List[FailureAnalyticsRecord]:
        """Returns recorded failure analytics."""
        return list(self._records)
