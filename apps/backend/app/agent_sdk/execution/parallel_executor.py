"""ParallelExecutor running multiple tasks concurrently or sequentially.
"""

import asyncio
from typing import Any, Callable, Coroutine, List, Optional

from app.agent_sdk.execution.context import ExecutionContext
from app.agent_sdk.execution.executor import Executor
from app.agent_sdk.execution.result import ExecutionResult


class ParallelExecutor:
    """Executes multi-task lists in parallel with concurrency semaphore rules."""

    def __init__(self, executor: Optional[Executor] = None) -> None:
        """Initializes ParallelExecutor.

        Args:
            executor: Active task executor instance.
        """
        self.executor = executor or Executor()

    async def run_parallel(
        self,
        tasks: List[Callable[[], Coroutine[Any, Any, Any]]],
        concurrency_limit: int = 5,
        context: Optional[ExecutionContext] = None,
    ) -> List[ExecutionResult]:
        """Runs tasks in parallel limiting active concurrency.

        Args:
            tasks: List of callables yielding coroutines.
            concurrency_limit: Concurrency limit.
            context: Execution context mapping.

        Returns:
            List of ExecutionResults in task order.
        """
        sem = asyncio.Semaphore(concurrency_limit)
        ctx = context or ExecutionContext(agent_name="Parallel", task_name="ParallelRun")

        async def worker(task_func: Callable[[], Coroutine[Any, Any, Any]]) -> ExecutionResult:
            async with sem:
                return await self.executor.execute(task_func, ctx)

        futures = [worker(task) for task in tasks]
        return list(await asyncio.gather(*futures))

    async def run_sequential(
        self,
        tasks: List[Callable[[], Coroutine[Any, Any, Any]]],
        context: Optional[ExecutionContext] = None,
    ) -> List[ExecutionResult]:
        """Runs tasks sequentially in order.

        Args:
            tasks: List of callables yielding coroutines.
            context: Execution context mapping.

        Returns:
            List of ExecutionResults.
        """
        results = []
        ctx = context or ExecutionContext(agent_name="Sequential", task_name="SeqRun")
        for task in tasks:
            res = await self.executor.execute(task, ctx)
            results.append(res)
        return results
