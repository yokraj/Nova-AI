"""Executor running single tasks targets wrapping tracing and middlewares.
"""

from datetime import datetime, timezone
import time
from typing import Any, Callable, Coroutine, List, Optional

from app.agent_sdk.execution.cancellation import CancellationToken
from app.agent_sdk.execution.context import ExecutionContext
from app.agent_sdk.execution.exceptions import CancelledExecutionError
from app.agent_sdk.execution.hooks import ExecutionHooks
from app.agent_sdk.execution.metrics import ExecutionMetrics
from app.agent_sdk.execution.middleware import ExecutionMiddleware
from app.agent_sdk.execution.result import ExecutionResult


class Executor:
    """Executes single task targets wrapping tracing, middlewares, and callbacks hooks."""

    def __init__(
        self,
        middlewares: Optional[List[ExecutionMiddleware]] = None,
        hooks: Optional[ExecutionHooks] = None,
        cancellation_token: Optional[CancellationToken] = None,
    ) -> None:
        """Initializes Executor.

        Args:
            middlewares: Middlewares list.
            hooks: Callbacks hooks container.
            cancellation_token: Cancellation listener token.
        """
        self.middlewares = middlewares or []
        self.hooks = hooks or ExecutionHooks()
        self.cancellation_token = cancellation_token or CancellationToken()

    async def execute(
        self,
        task_func: Callable[..., Coroutine[Any, Any, Any]],
        context: ExecutionContext,
        *args: Any,
        **kwargs: Any,
    ) -> ExecutionResult:
        """Executes coroutine task, wrapping triggers with metrics and middleware.

        Args:
            task_func: Target coroutine function.
            context: Context tracking.
            args: Mapped arguments.
            kwargs: Mapped keywords arguments.

        Returns:
            Unified execution result outcome.
        """
        start_time = time.time()
        context.started_at = datetime.now(timezone.utc)
        logs = []

        try:
            self.cancellation_token.throw_if_cancelled()

            for mw in self.middlewares:
                await mw.before_execution(context)

            await self.hooks.trigger_on_start(context)

            # Preprocess inputs using middleware before_step hook
            input_val = args[0] if args else None
            for mw in self.middlewares:
                input_val = await mw.before_step(context, context.task_name, input_val)

            if args:
                args_list = list(args)
                args_list[0] = input_val
                args = tuple(args_list)

            # Execution
            result_payload = await task_func(*args, **kwargs)

            # Postprocess outputs using middleware after_step hook
            for mw in self.middlewares:
                result_payload = await mw.after_step(context, context.task_name, result_payload)

            self.cancellation_token.throw_if_cancelled()

            duration = time.time() - start_time
            metrics = ExecutionMetrics(execution_time=duration)
            res = ExecutionResult(
                success=True,
                status="completed",
                result=result_payload,
                duration=duration,
                metrics=metrics,
                logs=logs,
            )

            for mw in self.middlewares:
                await mw.after_execution(context, res)

            await self.hooks.trigger_on_complete(context, res)
            return res

        except CancelledExecutionError as e:
            duration = time.time() - start_time
            res = ExecutionResult(
                success=False,
                status="cancelled",
                error=str(e),
                duration=duration,
                metrics=ExecutionMetrics(execution_time=duration),
            )
            await self.hooks.trigger_on_cancel(context)
            await self.hooks.trigger_on_complete(context, res)
            return res

        except Exception as e:
            duration = time.time() - start_time
            res = ExecutionResult(
                success=False,
                status="failed",
                error=str(e),
                duration=duration,
                metrics=ExecutionMetrics(execution_time=duration),
            )

            recovered = None
            for mw in self.middlewares:
                rec_res = await mw.error_handler(context, e)
                if rec_res is not None:
                    recovered = rec_res

            if recovered:
                return recovered

            await self.hooks.trigger_on_failure(context, e)
            await self.hooks.trigger_on_complete(context, res)
            return res

    def execute_sync(
        self, sync_func: Callable[..., Any], context: ExecutionContext, *args: Any, **kwargs: Any
    ) -> ExecutionResult:
        """Executes a synchronous task blocking execution thread.

        Args:
            sync_func: Target synchronous task.
            context: Context tracking.
            args: Positional arguments.
            kwargs: Keyword arguments.

        Returns:
            Unified execution result outcome.
        """
        start_time = time.time()
        context.started_at = datetime.now(timezone.utc)
        try:
            res_val = sync_func(*args, **kwargs)
            duration = time.time() - start_time
            return ExecutionResult(
                success=True,
                status="completed",
                result=res_val,
                duration=duration,
                metrics=ExecutionMetrics(execution_time=duration),
            )
        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                success=False,
                status="failed",
                error=str(e),
                duration=duration,
                metrics=ExecutionMetrics(execution_time=duration),
            )
