"""AgentScheduler managing agent execution pipelines.
"""

import asyncio
from datetime import datetime, UTC
import time
from typing import Dict, List, Optional
import uuid

from app.agents.bus.request import AgentRequest
from app.agents.bus.routing import RoutingService
from app.agents.scheduler.exceptions import JobNotFoundError, JobTimeoutError, RetryLimitExceededError
from app.agents.scheduler.job import AgentJob
from app.agents.scheduler.job_queue import JobQueue
from app.agents.scheduler.job_result import JobResult
from app.agents.scheduler.priority import Priority
from app.agents.scheduler.retry_policy import RetryPolicy
from app.agents.scheduler.status import JobStatus


class AgentScheduler:
    """The central enterprise scheduler coordinating agent execution runs."""

    def __init__(self, routing_service: RoutingService, queue: Optional[JobQueue] = None) -> None:
        """Initializes AgentScheduler.

        Args:
            routing_service: Router for executing requests.
            queue: Internal priority-ordered JobQueue.
        """
        self.routing_service = routing_service
        self.queue = queue or JobQueue()
        self._jobs: Dict[uuid.UUID, AgentJob] = {}
        self._results: Dict[uuid.UUID, JobResult] = {}

    def submit(
        self,
        agent_id: uuid.UUID,
        request: AgentRequest,
        priority: Priority = Priority.NORMAL,
        retry_policy: Optional[RetryPolicy] = None,
        timeout: Optional[float] = None,
    ) -> AgentJob:
        """Submits an agent task to run immediately, adding it to the queue.

        Args:
            agent_id: Target agent identifier.
            request: AgentRequest payload.
            priority: Priority tier.
            retry_policy: Custom retry guidelines.
            timeout: Optional maximum duration limit.

        Returns:
            The created and queued AgentJob.
        """
        job = AgentJob(
            agent_id=agent_id,
            request=request,
            priority=priority,
            scheduled_time=datetime.now(UTC),
            timeout=timeout,
            status=JobStatus.PENDING,
            retry_policy=retry_policy or RetryPolicy(),
        )
        self._jobs[job.job_id] = job
        self.queue.enqueue(job)
        return job

    def schedule(
        self,
        agent_id: uuid.UUID,
        request: AgentRequest,
        scheduled_time: datetime,
        priority: Priority = Priority.NORMAL,
        retry_policy: Optional[RetryPolicy] = None,
        timeout: Optional[float] = None,
    ) -> AgentJob:
        """Schedules a job to run at a specific future timestamp.

        Args:
            agent_id: Target agent identifier.
            request: AgentRequest payload.
            scheduled_time: Timestamp to execute the job.
            priority: Priority tier.
            retry_policy: Custom retry guidelines.
            timeout: Optional maximum duration limit.

        Returns:
            The created and scheduled AgentJob.
        """
        job = AgentJob(
            agent_id=agent_id,
            request=request,
            priority=priority,
            scheduled_time=scheduled_time,
            timeout=timeout,
            status=JobStatus.SCHEDULED,
            retry_policy=retry_policy or RetryPolicy(),
        )
        self._jobs[job.job_id] = job
        self.queue.enqueue(job)
        return job

    def cancel(self, job_id: uuid.UUID) -> None:
        """Cancels a pending or scheduled job.

        Args:
            job_id: ID of the job to cancel.

        Raises:
            JobNotFoundError: If job is not tracked.
        """
        if job_id not in self._jobs:
            raise JobNotFoundError(f"Job with ID '{job_id}' not found.")

        job = self._jobs[job_id]
        if job.status in (JobStatus.PENDING, JobStatus.SCHEDULED):
            self.queue.remove(job_id)
            job.status = JobStatus.CANCELLED
        else:
            # If already running or completed/failed, we cannot cancel
            pass

    def retry(self, job_id: uuid.UUID) -> None:
        """Forces a retry of a failed or timed out job manually, putting it back to pending.

        Args:
            job_id: ID of the job to retry.

        Raises:
            JobNotFoundError: If job is not tracked.
        """
        if job_id not in self._jobs:
            raise JobNotFoundError(f"Job with ID '{job_id}' not found.")

        job = self._jobs[job_id]
        job.status = JobStatus.PENDING
        job.retry_count = 0
        self.queue.enqueue(job)

    async def execute(self, job: AgentJob) -> JobResult:
        """Executes a single job, implementing timeout blocks and retry policies.

        Args:
            job: AgentJob to execute.

        Returns:
            JobResult of the execution run.
        """
        self.queue.remove(job.job_id)
        job.status = JobStatus.RUNNING

        retries_attempted = 0
        errors_logged = []
        start_time = time.perf_counter()
        success = False
        output = None

        while True:
            try:
                if job.timeout:
                    response = await asyncio.wait_for(
                        self.routing_service.route_request(job.request),
                        timeout=job.timeout,
                    )
                else:
                    response = await self.routing_service.route_request(job.request)

                if response.success:
                    success = True
                    output = response.payload
                    job.status = JobStatus.COMPLETED
                    break
                else:
                    raise Exception(response.payload.get("error", "Agent execution returned success=False."))
            except asyncio.TimeoutError:
                errors_logged.append("Job execution timed out.")
                job.status = JobStatus.TIMEOUT
            except Exception as e:
                errors_logged.append(str(e))
                job.status = JobStatus.FAILED

            # Evaluate retry policy
            if retries_attempted < job.retry_policy.max_retries:
                retries_attempted += 1
                job.retry_count = retries_attempted

                delay = job.retry_policy.retry_delay
                if job.retry_policy.exponential_backoff:
                    delay = delay * (2 ** (retries_attempted - 1))

                await asyncio.sleep(delay)
                job.status = JobStatus.RUNNING  # Reset for next run attempt
            else:
                break

        execution_time = time.perf_counter() - start_time
        result = JobResult(
            success=success,
            output=output,
            execution_time=execution_time,
            retries=retries_attempted,
            errors=errors_logged,
        )
        self._results[job.job_id] = result
        return result

    async def execute_all(self) -> List[JobResult]:
        """Executes all currently due pending and scheduled jobs in the queue.

        Returns:
            List of JobResults for all executed jobs.
        """
        now = datetime.now(UTC)
        results = []

        all_jobs = self.queue.list_jobs()
        due_jobs = [j for j in all_jobs if j.scheduled_time <= now]

        for job in due_jobs:
            self.queue.remove(job.job_id)
            res = await self.execute(job)
            results.append(res)

        return results

    def pending_jobs(self) -> List[AgentJob]:
        """Returns all jobs currently queued and pending/scheduled.

        Returns:
            List of pending AgentJob models.
        """
        return [
            j
            for j in self._jobs.values()
            if j.status in (JobStatus.PENDING, JobStatus.SCHEDULED)
        ]

    def running_jobs(self) -> List[AgentJob]:
        """Returns all currently running jobs.

        Returns:
            List of running AgentJob models.
        """
        return [j for j in self._jobs.values() if j.status == JobStatus.RUNNING]

    def completed_jobs(self) -> List[AgentJob]:
        """Returns all completed jobs.

        Returns:
            List of completed AgentJob models.
        """
        return [j for j in self._jobs.values() if j.status == JobStatus.COMPLETED]
