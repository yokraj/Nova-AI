"""Unified Scheduler Runtime consolidating all subsystem schedulers into one priority cron/timer queue.
"""

from typing import Any, Dict, List, Optional
from app.ai.os_runtime.models import SchedulerJob


class UnifiedSchedulerRuntime:
    """Unified scheduler consolidating Mission, Workflow, Reminder, Learning, Automation, Health, Research, and Backup schedulers."""

    def __init__(self) -> None:
        self._jobs: List[SchedulerJob] = []

    async def schedule_job(
        self,
        name: str,
        category: str = "mission",
        cron_expression: Optional[str] = None,
        interval_seconds: Optional[float] = None,
    ) -> SchedulerJob:
        """Schedules unified job in OS priority queue."""
        job = SchedulerJob(
            name=name,
            category=category,
            cron_expression=cron_expression,
            interval_seconds=interval_seconds,
        )
        self._jobs.append(job)
        return job

    def list_jobs(self) -> List[SchedulerJob]:
        """Lists active scheduled jobs."""
        return list(self._jobs)
