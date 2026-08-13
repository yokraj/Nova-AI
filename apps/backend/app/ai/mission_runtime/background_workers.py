"""Background Workers managing concurrent thread pool execution for long-running missions.
"""

from typing import Any, Dict, List
from app.ai.mission_runtime.interfaces import IBackgroundWorkers
from app.ai.mission_runtime.models import WorkerStatus


class BackgroundWorkers(IBackgroundWorkers):
    """Background Workers managing concurrent execution threads."""

    def __init__(self, max_workers: int = 5) -> None:
        self.max_workers = max_workers
        self._workers: Dict[str, WorkerStatus] = {}

    async def dispatch_worker(self, mission_id: str) -> WorkerStatus:
        """Dispatches an autonomous background worker for a mission.

        Args:
            mission_id: Target mission ID string.

        Returns:
            WorkerStatus enum instance.
        """
        self._workers[mission_id] = WorkerStatus.WORKING
        return WorkerStatus.WORKING

    async def stop_worker(self, mission_id: str) -> WorkerStatus:
        """Stops background worker."""
        if mission_id in self._workers:
            self._workers[mission_id] = WorkerStatus.STOPPED
        return WorkerStatus.STOPPED

    def get_active_workers_count(self) -> int:
        """Returns count of active working threads."""
        return sum(1 for status in self._workers.values() if status == WorkerStatus.WORKING)
