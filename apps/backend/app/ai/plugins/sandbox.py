"""Sandbox providing isolated, timeout-guarded execution of plugin capabilities."""

import inspect
import time
from typing import Any
import anyio
import structlog

from app.ai.plugins.exceptions import SandboxViolationError
from app.ai.plugins.interfaces import ISandbox
from app.ai.plugins.models import ExecutionRequest, ExecutionResult

logger = structlog.get_logger("sandbox")


class PluginSandbox(ISandbox):
    """Executes plugin handlers within a timeout-enforced async sandbox."""

    def __init__(self, timeout_seconds: float = 30.0) -> None:
        self.default_timeout = timeout_seconds

    async def execute(
        self,
        request: ExecutionRequest,
        handler: Any,
    ) -> ExecutionResult:
        """Run handler asynchronously with timeout isolation."""
        start_time = time.perf_counter()
        timeout = request.timeout_seconds or self.default_timeout

        try:
            with anyio.fail_after(timeout):
                if inspect.iscoroutinefunction(handler):
                    result = await handler()
                else:
                    result = handler()

            duration = round(time.perf_counter() - start_time, 4)
            return ExecutionResult(
                request_id=request.request_id,
                plugin_id=request.plugin_id,
                capability=request.capability,
                success=True,
                data=result,
                execution_time_seconds=duration,
            )
        except TimeoutError as err:
            duration = round(time.perf_counter() - start_time, 4)
            raise SandboxViolationError(
                f"Execution of capability '{request.capability}' on plugin '{request.plugin_id}' "
                f"timed out after {timeout}s."
            ) from err
        except Exception as err:
            duration = round(time.perf_counter() - start_time, 4)
            logger.error("Sandbox caught execution exception", plugin=request.plugin_id, error=str(err))
            return ExecutionResult(
                request_id=request.request_id,
                plugin_id=request.plugin_id,
                capability=request.capability,
                success=False,
                error=str(err),
                execution_time_seconds=duration,
            )
