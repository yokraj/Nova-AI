"""Workflow Tracker monitoring active task progress and approvals lifecycle.
"""

import structlog
from typing import Dict, Any, List

logger = structlog.get_logger("workflow_tracker")

class WorkflowTracker:
    """Tracks task allocations, progress ratios, and pending approval queues."""

    def __init__(self) -> None:
        self.allocations: Dict[str, str] = {}
        self.progress_ratios: Dict[str, float] = {}
        self.approval_queue: List[str] = []

    def assign(self, task_id: str, agent_id: str) -> None:
        """Assigns task to agent."""
        self.allocations[task_id] = agent_id
        self.progress_ratios[task_id] = 0.0

    def report_progress(self, task_id: str, percent: float) -> None:
        """Updates progress percentage."""
        self.progress_ratios[task_id] = percent

    def queue_approval(self, task_id: str) -> None:
        """Queues task for approval."""
        if task_id not in self.approval_queue:
            self.approval_queue.append(task_id)

    def complete(self, task_id: str) -> None:
        """Marks task as complete, clearing approval requests."""
        if task_id in self.approval_queue:
            self.approval_queue.remove(task_id)
        self.progress_ratios[task_id] = 100.0
