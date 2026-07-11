"""ExecutionMiddleware base class definition.
"""

from typing import Any, Optional

from app.agent_sdk.execution.context import ExecutionContext
from app.agent_sdk.execution.result import ExecutionResult


class ExecutionMiddleware:
    """Base middleware handler tracing pipeline hooks."""

    async def before_execution(self, context: ExecutionContext) -> None:
        """Hook called before starting runner pipeline execution.

        Args:
            context: Execution context parameter.
        """
        pass

    async def after_execution(self, context: ExecutionContext, result: ExecutionResult) -> None:
        """Hook called after runner pipeline execution completes.

        Args:
            context: Execution context parameter.
            result: Result payload outcome.
        """
        pass

    async def before_step(self, context: ExecutionContext, step_name: str, step_input: Any) -> Any:
        """Hook called before executing an individual step.

        Args:
            context: Execution context parameter.
            step_name: Identifier of the step.
            step_input: Input arguments.

        Returns:
            Preprocessed input payload.
        """
        return step_input

    async def after_step(self, context: ExecutionContext, step_name: str, step_output: Any) -> Any:
        """Hook called after executing an individual step.

        Args:
            context: Execution context parameter.
            step_name: Identifier of the step.
            step_output: Output value.

        Returns:
            Postprocessed output payload.
        """
        return step_output

    async def error_handler(self, context: ExecutionContext, exception: Exception) -> Optional[ExecutionResult]:
        """Hook to capture, log, or recover from exceptions.

        Args:
            context: Execution context parameter.
            exception: Active exception trigger.

        Returns:
            Optional recovered ExecutionResult payload, or None.
        """
        return None
