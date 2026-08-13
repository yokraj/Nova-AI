"""Assistant Metrics Tracker recording telemetry metrics."""

import structlog

from app.ai.assistant.models import AssistantMetrics

logger = structlog.get_logger("assistant_metrics")


class AssistantMetricsTracker:
    """Tracks telemetry metrics for Personal Assistant Engine."""

    def __init__(self) -> None:
        self._plans_generated = 0
        self._reminders_created = 0
        self._tasks_managed = 0
        self._meetings_prepared = 0
        self._goals_tracked = 0
        self._habits_logged = 0
        self._suggestions_count = 0

    def record_plan(self) -> None:
        self._plans_generated += 1

    def record_reminder(self) -> None:
        self._reminders_created += 1

    def record_task(self) -> None:
        self._tasks_managed += 1

    def record_meeting_prep(self) -> None:
        self._meetings_prepared += 1

    def record_goal(self) -> None:
        self._goals_tracked += 1

    def record_habit(self) -> None:
        self._habits_logged += 1

    def record_suggestion(self) -> None:
        self._suggestions_count += 1

    def get_metrics(self) -> AssistantMetrics:
        """Get metrics snapshot."""
        return AssistantMetrics(
            total_plans_generated=self._plans_generated,
            reminders_created=self._reminders_created,
            tasks_managed=self._tasks_managed,
            meetings_prepared=self._meetings_prepared,
            goals_tracked=self._goals_tracked,
            habits_logged=self._habits_logged,
            proactive_suggestions_count=self._suggestions_count,
        )
