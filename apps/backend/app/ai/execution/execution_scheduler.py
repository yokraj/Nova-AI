"""Execution Scheduler managing step timeouts, retries, and execution timing."""

import inspect
import time
from typing import Any, Callable, Optional
import anyio
import structlog

from app.ai.execution.exceptions import StepFailedError
from app.ai.execution.models import ExecutionStep, StepStatus

logger = structlog.get_logger("execution_scheduler")


class ExecutionScheduler:
    """Schedules step execution with AnyIO timeout enforcement and retry handling."""

    def __init__(self, default_timeout: float = 120.0) -> None:
        self.default_timeout = default_timeout

    async def schedule_step(
        self,
        step: ExecutionStep,
        func: Callable[[], Any],
    ) -> Any:
        """Run step function with timeout and retry handling."""
        timeout = self.default_timeout
        attempt = 0
        last_err: Optional[Exception] = None

        while attempt <= step.max_retries:
            attempt += 1
            step.retry_count = attempt - 1
            start_time = time.perf_counter()

            try:
                with anyio.fail_after(timeout):
                    if inspect.iscoroutinefunction(func):
                        result = await func()
                    else:
                        result = func()

                step.duration_seconds = round(time.perf_counter() - start_time, 4)
                step.status = StepStatus.COMPLETED
                return result

            except Exception as err:
                step.duration_seconds = round(time.perf_counter() - start_time, 4)
                last_err = err
                logger.warning(
                    "Step attempt failed",
                    step_id=step.step_id,
                    attempt=attempt,
                    max_retries=step.max_retries,
                    error=str(err),
                )
                if attempt <= step.max_retries:
                    step.status = StepStatus.RETRIED
                    await anyio.sleep(0.5)

        step.status = StepStatus.FAILED
        step.error = str(last_err)
        raise StepFailedError(f"Step '{step.name}' failed after {step.max_retries + 1} attempts: {last_err}") from last_err


from typing import Optional  # noqa: E402
