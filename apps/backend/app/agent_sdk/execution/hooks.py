"""ExecutionHooks defining execution callbacks triggers.
"""

from typing import Any, Callable, Coroutine, List

from app.agent_sdk.execution.context import ExecutionContext
from app.agent_sdk.execution.result import ExecutionResult


class ExecutionHooks:
    """Callbacks registering on execution events."""

    def __init__(self) -> None:
        """Initializes ExecutionHooks."""
        self._on_start_callbacks: List[Callable[[ExecutionContext], Coroutine[Any, Any, None]]] = []
        self._on_complete_callbacks: List[
            Callable[[ExecutionContext, ExecutionResult], Coroutine[Any, Any, None]]
        ] = []
        self._on_failure_callbacks: List[Callable[[ExecutionContext, Exception], Coroutine[Any, Any, None]]] = []
        self._on_cancel_callbacks: List[Callable[[ExecutionContext], Coroutine[Any, Any, None]]] = []

    def register_on_start(self, callback: Callable[[ExecutionContext], Coroutine[Any, Any, None]]) -> None:
        """Registers callback for on_start.

        Args:
            callback: Coroutine callable.
        """
        self._on_start_callbacks.append(callback)

    def register_on_complete(
        self, callback: Callable[[ExecutionContext, ExecutionResult], Coroutine[Any, Any, None]]
    ) -> None:
        """Registers callback for on_complete.

        Args:
            callback: Coroutine callable.
        """
        self._on_complete_callbacks.append(callback)

    def register_on_failure(
        self, callback: Callable[[ExecutionContext, Exception], Coroutine[Any, Any, None]]
    ) -> None:
        """Registers callback for on_failure.

        Args:
            callback: Coroutine callable.
        """
        self._on_failure_callbacks.append(callback)

    def register_on_cancel(self, callback: Callable[[ExecutionContext], Coroutine[Any, Any, None]]) -> None:
        """Registers callback for on_cancel.

        Args:
            callback: Coroutine callable.
        """
        self._on_cancel_callbacks.append(callback)

    async def trigger_on_start(self, context: ExecutionContext) -> None:
        """Triggers on_start hook.

        Args:
            context: Execution context parameter.
        """
        for cb in self._on_start_callbacks:
            await cb(context)

    async def trigger_on_complete(self, context: ExecutionContext, result: ExecutionResult) -> None:
        """Triggers on_complete hook.

        Args:
            context: Execution context parameter.
            result: Result payload outcome.
        """
        for cb in self._on_complete_callbacks:
            await cb(context, result)

    async def trigger_on_failure(self, context: ExecutionContext, exception: Exception) -> None:
        """Triggers on_failure hook.

        Args:
            context: Execution context parameter.
            exception: Active exception trigger.
        """
        for cb in self._on_failure_callbacks:
            await cb(context, exception)

    async def trigger_on_cancel(self, context: ExecutionContext) -> None:
        """Triggers on_cancel hook.

        Args:
            context: Execution context parameter.
        """
        for cb in self._on_cancel_callbacks:
            await cb(context)
