"""Pipeline orchestrating sequential chains of steps execution.
"""

from datetime import datetime, timezone
import time
from typing import Any, Callable, Coroutine, List, Optional, Tuple

from app.agent_sdk.execution.context import ExecutionContext
from app.agent_sdk.execution.exceptions import PipelineError
from app.agent_sdk.execution.executor import Executor
from app.agent_sdk.execution.metrics import ExecutionMetrics
from app.agent_sdk.execution.result import ExecutionResult


class Pipeline:
    """Orchestrates structured step chains sequentially."""

    def __init__(self, context: ExecutionContext, executor: Optional[Executor] = None) -> None:
        """Initializes Pipeline.

        Args:
            context: Execution context payload.
            executor: Active task executor instance.
        """
        self.context = context
        self.executor = executor or Executor()
        self._steps: List[Tuple[str, Callable[[Any], Coroutine[Any, Any, Any]]]] = []

    def register_step(self, step_name: str, step_coro: Callable[[Any], Coroutine[Any, Any, Any]]) -> None:
        """Appends step execution to the queue.

        Args:
            step_name: Identifier of the step.
            step_coro: Coroutine callable taking one input and returning output.
        """
        self._steps.append((step_name, step_coro))

    def remove_step(self, step_name: str) -> None:
        """Removes step from the queue by name.

        Args:
            step_name: Identifier of the step.
        """
        self._steps = [step for step in self._steps if step[0] != step_name]

    async def execute(self, initial_input: Any) -> ExecutionResult:
        """Executes pipeline steps sequentially.

        Args:
            initial_input: Initial input arguments passed into step 1.

        Returns:
            Unified execution result.
        """
        start_time = time.time()
        self.context.started_at = datetime.now(timezone.utc)
        current_data = initial_input
        logs = []

        try:
            await self.before_execute()

            for step_name, step_coro in self._steps:
                self.executor.cancellation_token.throw_if_cancelled()
                logs.append(f"Starting step: {step_name}")

                # Configure task name in context dynamically for middleware tracing
                self.context.task_name = step_name
                step_res = await self.executor.execute(step_coro, self.context, current_data)

                if not step_res.success:
                    raise PipelineError(f"Pipeline step '{step_name}' failed: {step_res.error}")

                current_data = step_res.result
                logs.append(f"Completed step: {step_name}")

            await self.after_execute()

            duration = time.time() - start_time
            self.context.completed_at = datetime.now(timezone.utc)
            return ExecutionResult(
                success=True,
                status="completed",
                result=current_data,
                duration=duration,
                metrics=ExecutionMetrics(execution_time=duration),
                logs=logs,
            )
        except Exception as e:
            duration = time.time() - start_time
            self.context.completed_at = datetime.now(timezone.utc)
            return ExecutionResult(
                success=False,
                status="failed",
                error=str(e),
                duration=duration,
                metrics=ExecutionMetrics(execution_time=duration),
                logs=logs,
            )

    async def before_execute(self) -> None:
        """Pipeline preprocessing hook."""
        pass

    async def after_execute(self) -> None:
        """Pipeline postprocessing hook."""
        pass
