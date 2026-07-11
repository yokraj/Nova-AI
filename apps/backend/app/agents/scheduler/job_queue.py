"""Priority-ordered task queue for AgentJobs.
"""

from typing import List, Optional
import uuid
from app.agents.scheduler.exceptions import JobNotFoundError
from app.agents.scheduler.job import AgentJob
from app.agents.scheduler.priority import Priority


class JobQueue:
    """A priority-ordered task queue for AgentJobs."""

    def __init__(self) -> None:
        """Initializes JobQueue."""
        self._jobs: List[AgentJob] = []

    def enqueue(self, job: AgentJob) -> None:
        """Adds a job to the queue, maintaining priority and scheduled_time order.

        Args:
            job: AgentJob to add.
        """
        self._jobs.append(job)
        self._sort_queue()

    def dequeue(self) -> Optional[AgentJob]:
        """Removes and returns the highest priority, scheduled job from the queue.

        Returns:
            The popped AgentJob instance, or None if queue is empty.
        """
        if not self._jobs:
            return None
        return self._jobs.pop(0)

    def peek(self) -> Optional[AgentJob]:
        """Returns the highest priority job without removing it from the queue.

        Returns:
            AgentJob at head of queue, or None.
        """
        if not self._jobs:
            return None
        return self._jobs[0]

    def remove(self, job_id: uuid.UUID) -> Optional[AgentJob]:
        """Removes a specific job from the queue by its ID.

        Args:
            job_id: ID of the job to remove.

        Returns:
            The removed AgentJob instance, or None if not found.
        """
        for index, job in enumerate(self._jobs):
            if job.job_id == job_id:
                return self._jobs.pop(index)
        return None

    def reprioritize(self, job_id: uuid.UUID, new_priority: Priority) -> None:
        """Updates the priority of an existing job and re-sorts the queue.

        Args:
            job_id: Target job identifier.
            new_priority: Priority level to apply.

        Raises:
            JobNotFoundError: If the job is not in the queue.
        """
        found = False
        for job in self._jobs:
            if job.job_id == job_id:
                job.priority = new_priority
                found = True
                break
        if not found:
            raise JobNotFoundError(f"Job with ID '{job_id}' not found in the queue.")
        self._sort_queue()

    def _sort_queue(self) -> None:
        """Sorts the queue primarily by priority rank (highest first) and scheduled_time (earliest first)."""
        self._jobs.sort(key=lambda j: j.scheduled_time)
        self._jobs.sort(key=lambda j: j.priority.rank, reverse=True)

    def list_jobs(self) -> List[AgentJob]:
        """Returns a list of all jobs currently in the queue.

        Returns:
            List of AgentJob models.
        """
        return list(self._jobs)
