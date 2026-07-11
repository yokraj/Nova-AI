"""Unit tests for the Enterprise Agent Scheduler subsystem.

Verifies job queue priority ordering, delayed execution scheduling, cancellation,
timeouts, retry policy backoff execution, and manual retries.
"""

import asyncio
from datetime import datetime, timedelta, UTC
from typing import Any, Dict, List
import uuid
import pytest

from app.agents import (
    AgentCapability,
    AgentContext,
    AgentDescriptor,
    AgentMetadata,
    AgentPermission,
    AgentRegistry,
    AgentResult,
    BaseAgent,
)
from app.agents.bus import AgentRequest, RoutingService
from app.agents.scheduler import (
    AgentScheduler,
    JobQueue,
    AgentJob,
    JobResult,
    Priority,
    JobStatus,
    RetryPolicy,
    JobNotFoundError,
)


class DummySchedulerAgent(BaseAgent):
    """Mock agent implementation for scheduler checking."""

    async def initialize(self) -> None:
        pass

    async def execute(self, context: AgentContext, prompt: str) -> AgentResult:
        if prompt == "timeout":
            await asyncio.sleep(1.0)
            return AgentResult(success=True, response="Timeout done", execution_time=1.0)
        elif prompt == "fail":
            return AgentResult(success=False, response="Failed run", execution_time=0.0)
        return AgentResult(success=True, response=f"Success: {prompt}", execution_time=0.05)

    async def shutdown(self) -> None:
        pass

    async def health(self) -> Dict[str, Any]:
        return {"status": "ok"}


@pytest.fixture
def scheduler_setup() -> AgentScheduler:
    """Fixture initializing AgentRegistry, RoutingService, and AgentScheduler with mock agents."""
    registry = AgentRegistry()
    routing = RoutingService(registry)
    scheduler = AgentScheduler(routing)

    meta_a = AgentMetadata(name="AgentA", description="first agent")
    agent_a = DummySchedulerAgent(meta_a)
    registry.register(agent_a)

    return scheduler


def test_job_queue_sorting() -> None:
    """Verifies that JobQueue dequeues items in descending priority, then ascending scheduled_time order."""
    queue = JobQueue()
    agent_id = uuid.uuid4()
    req = AgentRequest(
        sender="System", receiver="AgentA", conversation_id=uuid.uuid4(), payload={}
    )

    now = datetime.now(UTC)
    job_low = AgentJob(
        agent_id=agent_id, request=req, priority=Priority.LOW, scheduled_time=now + timedelta(seconds=1)
    )
    job_normal_earlier = AgentJob(
        agent_id=agent_id, request=req, priority=Priority.NORMAL, scheduled_time=now - timedelta(seconds=10)
    )
    job_normal_later = AgentJob(
        agent_id=agent_id, request=req, priority=Priority.NORMAL, scheduled_time=now + timedelta(seconds=10)
    )
    job_critical = AgentJob(
        agent_id=agent_id, request=req, priority=Priority.CRITICAL, scheduled_time=now
    )

    # Enqueue in randomized priority order
    queue.enqueue(job_low)
    queue.enqueue(job_normal_later)
    queue.enqueue(job_normal_earlier)
    queue.enqueue(job_critical)

    # Verify dequeue order:
    # 1. CRITICAL
    # 2. NORMAL (earlier scheduled_time first)
    # 3. NORMAL (later)
    # 4. LOW
    assert queue.dequeue().job_id == job_critical.job_id
    assert queue.dequeue().job_id == job_normal_earlier.job_id
    assert queue.dequeue().job_id == job_normal_later.job_id
    assert queue.dequeue().job_id == job_low.job_id


@pytest.mark.anyio
async def test_scheduler_submission_and_execution(scheduler_setup: AgentScheduler) -> None:
    """Verifies submit (immediate) and schedule (delayed) job creation and executions."""
    scheduler = scheduler_setup
    agent_a_id = [d.id for d in scheduler.routing_service.registry.list() if d.name == "AgentA"][0]

    req_immed = AgentRequest(
        sender="System", receiver="AgentA", conversation_id=uuid.uuid4(), payload={"prompt": "run_now"}
    )
    job_immed = scheduler.submit(agent_a_id, req_immed, priority=Priority.HIGH)
    assert job_immed.status == JobStatus.PENDING

    # Run immediate
    results = await scheduler.execute_all()
    assert len(results) == 1
    assert results[0].success is True
    assert results[0].output["response"] == "Success: run_now"
    assert job_immed.status == JobStatus.COMPLETED

    # Future Schedule
    req_future = AgentRequest(
        sender="System", receiver="AgentA", conversation_id=uuid.uuid4(), payload={"prompt": "run_future"}
    )
    future_time = datetime.now(UTC) + timedelta(hours=1)
    job_future = scheduler.schedule(agent_a_id, req_future, scheduled_time=future_time)
    assert job_future.status == JobStatus.SCHEDULED

    # Verify execute_all does NOT execute future scheduled jobs
    results_future = await scheduler.execute_all()
    assert len(results_future) == 0
    assert job_future.status == JobStatus.SCHEDULED
    assert len(scheduler.pending_jobs()) == 1


@pytest.mark.anyio
async def test_scheduler_cancellation(scheduler_setup: AgentScheduler) -> None:
    """Verifies that cancel shifts pending/scheduled jobs to CANCELLED state and removes them from queue."""
    scheduler = scheduler_setup
    agent_a_id = [d.id for d in scheduler.routing_service.registry.list() if d.name == "AgentA"][0]

    req = AgentRequest(
        sender="System", receiver="AgentA", conversation_id=uuid.uuid4(), payload={"prompt": "cancel_me"}
    )
    job = scheduler.submit(agent_a_id, req)
    assert job.status == JobStatus.PENDING

    scheduler.cancel(job.job_id)
    assert job.status == JobStatus.CANCELLED
    assert len(scheduler.queue.list_jobs()) == 0

    with pytest.raises(JobNotFoundError):
        scheduler.cancel(uuid.uuid4())


@pytest.mark.anyio
async def test_scheduler_timeout(scheduler_setup: AgentScheduler) -> None:
    """Verifies timeout policy constraints failed job runs with TIMEOUT status."""
    scheduler = scheduler_setup
    agent_a_id = [d.id for d in scheduler.routing_service.registry.list() if d.name == "AgentA"][0]

    req = AgentRequest(
        sender="System", receiver="AgentA", conversation_id=uuid.uuid4(), payload={"prompt": "timeout"}
    )
    job = scheduler.submit(agent_a_id, req, timeout=0.1)  # Agent sleeps 1s, job limit is 0.1s
    job.retry_policy.max_retries = 0  # No retries for timeout test

    result = await scheduler.execute(job)
    assert result.success is False
    assert job.status == JobStatus.TIMEOUT
    assert "timed out" in result.errors[0]


@pytest.mark.anyio
async def test_scheduler_retry_policy(scheduler_setup: AgentScheduler) -> None:
    """Verifies retry guidelines apply backoff pauses on failed job executions."""
    scheduler = scheduler_setup
    agent_a_id = [d.id for d in scheduler.routing_service.registry.list() if d.name == "AgentA"][0]

    req = AgentRequest(
        sender="System", receiver="AgentA", conversation_id=uuid.uuid4(), payload={"prompt": "fail"}
    )
    policy = RetryPolicy(max_retries=2, retry_delay=0.05, exponential_backoff=False)
    job = scheduler.submit(agent_a_id, req, retry_policy=policy)

    result = await scheduler.execute(job)
    assert result.success is False
    assert result.retries == 2
    assert job.retry_count == 2
    assert job.status == JobStatus.FAILED


@pytest.mark.anyio
async def test_scheduler_manual_retry(scheduler_setup: AgentScheduler) -> None:
    """Verifies that retry forces failed/timeout tasks back into pending status in the queue."""
    scheduler = scheduler_setup
    agent_a_id = [d.id for d in scheduler.routing_service.registry.list() if d.name == "AgentA"][0]

    req = AgentRequest(
        sender="System", receiver="AgentA", conversation_id=uuid.uuid4(), payload={"prompt": "fail"}
    )
    job = scheduler.submit(agent_a_id, req)
    job.retry_policy.max_retries = 0

    await scheduler.execute(job)
    assert job.status == JobStatus.FAILED
    assert len(scheduler.queue.list_jobs()) == 0

    scheduler.retry(job.job_id)
    assert job.status == JobStatus.PENDING
    assert len(scheduler.queue.list_jobs()) == 1
