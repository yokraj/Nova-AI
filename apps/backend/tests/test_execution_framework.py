"""Unit tests for the Agent SDK Execution Framework.

Verifies pipeline chaining, retry engines, timeouts, parallel execution limits,
cancellation tokens, progress updates, background runner tasks, and middleware hooks.
"""

import asyncio
import time
from typing import Any, Dict
import pytest

from app.agent_sdk.execution import (
    BackgroundRunner,
    CancellationToken,
    CancelledExecutionError,
    ExecutionContext,
    ExecutionHooks,
    ExecutionMetrics,
    ExecutionMiddleware,
    ExecutionResult,
    Executor,
    ParallelExecutor,
    Pipeline,
    PipelineError,
    ProgressTracker,
    RetryEngine,
    RetryExceededError,
    TimeoutError,
    TimeoutManager,
)


@pytest.mark.anyio
async def test_pipeline_execution() -> None:
    """Verifies pipeline step execution executes sequentially."""
    ctx = ExecutionContext(agent_name="SoftwareAgent", task_name="PipelineTest")

    async def step_one(input_val: int) -> int:
        return input_val + 10

    async def step_two(input_val: int) -> int:
        return input_val * 2

    pipeline = Pipeline(ctx)
    pipeline.register_step("AddTen", step_one)
    pipeline.register_step("MultiplyTwo", step_two)

    # (5 + 10) * 2 = 30
    res = await pipeline.execute(5)
    assert res.success is True
    assert res.result == 30
    assert "Starting step: AddTen" in res.logs
    assert "Completed step: MultiplyTwo" in res.logs


@pytest.mark.anyio
async def test_retry_engine() -> None:
    """Verifies RetryEngine handles backoffs and throws when attempts limit exceeded."""
    attempts = 0

    async def transient_fail() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Transient error")
        return "success"

    engine = RetryEngine(max_attempts=3, backoff_factor=1.1, initial_delay=0.1)
    res = await engine.execute(transient_fail)
    assert res == "success"
    assert attempts == 3

    # Permanent failure check
    async def permanent_fail() -> None:
        raise ValueError("Permanent error")

    engine_fail = RetryEngine(max_attempts=2, backoff_factor=1.1, initial_delay=0.1)
    with pytest.raises(RetryExceededError):
        await engine_fail.execute(permanent_fail)


@pytest.mark.anyio
async def test_timeout_manager() -> None:
    """Verifies TimeoutManager raises TimeoutError when execution limit is reached."""
    manager = TimeoutManager()

    async def slow_task() -> None:
        await asyncio.sleep(2.0)

    with pytest.raises(TimeoutError):
        await manager.execute_with_timeout(slow_task(), timeout_seconds=0.2)

    # Remaining time check
    assert manager.remaining_time() == 0.0


@pytest.mark.anyio
async def test_parallel_executor() -> None:
    """Verifies ParallelExecutor runs multiple task collections concurrently."""
    parallel = ParallelExecutor()

    async def task_one() -> str:
        await asyncio.sleep(0.1)
        return "one"

    async def task_two() -> str:
        await asyncio.sleep(0.1)
        return "two"

    res_list = await parallel.run_parallel([task_one, task_two], concurrency_limit=2)
    assert len(res_list) == 2
    assert res_list[0].success is True
    assert res_list[0].result == "one"
    assert res_list[1].result == "two"


@pytest.mark.anyio
async def test_cancellation_token() -> None:
    """Verifies CancellationToken aborts pending executions."""
    token = CancellationToken()
    executor = Executor(cancellation_token=token)
    ctx = ExecutionContext(agent_name="Agent", task_name="CancelTest")

    async def long_task() -> str:
        return "finished"

    token.cancel()
    res = await executor.execute(long_task, ctx)
    assert res.success is False
    assert res.status == "cancelled"
    assert "Execution cancelled" in res.error


def test_progress_tracker() -> None:
    """Verifies ProgressTracker percentage math and estimations."""
    tracker = ProgressTracker()
    tracker.start(total_steps=10)

    tracker.update(step=5, message="Halfway there")
    assert tracker.percentage() == 50.0

    tracker.complete(message="Completed")
    assert tracker.percentage() == 100.0
    assert tracker.estimated_remaining() == 0.0


@pytest.mark.anyio
async def test_background_runner() -> None:
    """Verifies BackgroundRunner job submission, query status, and cancellation."""
    runner = BackgroundRunner()

    async def bg_task() -> None:
        await asyncio.sleep(2.0)

    job_id = runner.submit(bg_task())
    assert job_id in runner.list_jobs()
    assert runner.status(job_id) == "running"

    runner.cancel(job_id)
    # Give generator loop turn to let task handle cancellation
    await asyncio.sleep(0.1)
    assert runner.status(job_id) == "cancelled"


@pytest.mark.anyio
async def test_middleware_and_hooks() -> None:
    """Verifies that ExecutionMiddleware hooks and hooks callbacks execute in sequence."""
    before_exec_called = False
    on_start_called = False
    step_input_modified = False
    step_output_modified = False

    class DummyMiddleware(ExecutionMiddleware):
        async def before_execution(self, context: ExecutionContext) -> None:
            nonlocal before_exec_called
            before_exec_called = True

        async def before_step(self, context: ExecutionContext, step_name: str, step_input: Any) -> Any:
            nonlocal step_input_modified
            step_input_modified = True
            return step_input + 5

        async def after_step(self, context: ExecutionContext, step_name: str, step_output: Any) -> Any:
            nonlocal step_output_modified
            step_output_modified = True
            return step_output * 2

    hooks = ExecutionHooks()

    async def on_start_cb(context: ExecutionContext) -> None:
        nonlocal on_start_called
        on_start_called = True

    hooks.register_on_start(on_start_cb)

    executor = Executor(middlewares=[DummyMiddleware()], hooks=hooks)
    ctx = ExecutionContext(agent_name="MiddlewareAgent", task_name="HookTest")

    async def double_task(input_val: int) -> int:
        return input_val

    # Input: 10 => Middleware before_step input: 10 + 5 = 15 => task returns 15
    # => Middleware after_step output: 15 * 2 = 30
    res = await executor.execute(double_task, ctx, 10)
    assert res.success is True
    assert res.result == 30
    assert before_exec_called is True
    assert on_start_called is True
    assert step_input_modified is True
    assert step_output_modified is True
