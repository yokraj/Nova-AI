"""BackgroundRunner managing tasks submitted asynchronously.
"""

import asyncio
from typing import Any, Dict, List
import uuid

from app.agent_sdk.execution.exceptions import ExecutionError


class BackgroundRunner:
    """Manages background task tasks executing asynchronously."""

    def __init__(self) -> None:
        """Initializes BackgroundRunner."""
        self._jobs: Dict[str, asyncio.Task[Any]] = {}

    def submit(self, coro: Any) -> str:
        """Submits task running in the background.

        Args:
            coro: Target task coroutine object.

        Returns:
            Unique string job identifier.
        """
        job_id = str(uuid.uuid4())
        task = asyncio.create_task(coro)
        self._jobs[job_id] = task
        return job_id

    def cancel(self, job_id: str) -> None:
        """Cancels a background job.

        Args:
            job_id: Identifier of target job.

        Raises:
            ExecutionError: If job ID is not found.
        """
        task = self._jobs.get(job_id)
        if not task:
            raise ExecutionError(f"Background job '{job_id}' not found.")
        task.cancel()

    def status(self, job_id: str) -> str:
        """Checks status of a background job.

        Args:
            job_id: Identifier of target job.

        Returns:
            Status string ('running', 'completed', 'cancelled', 'failed').

        Raises:
            ExecutionError: If job ID is not found.
        """
        task = self._jobs.get(job_id)
        if not task:
            raise ExecutionError(f"Background job '{job_id}' not found.")

        if task.cancelled():
            return "cancelled"
        if task.done():
            if task.exception():
                return "failed"
            return "completed"
        return "running"

    def list_jobs(self) -> List[str]:
        """Lists active and completed job identifiers.

        Returns:
            List of job ID strings.
        """
        return list(self._jobs.keys())
