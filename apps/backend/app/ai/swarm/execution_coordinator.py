"""Execution Coordinator managing wave-by-wave execution of task DAGs."""

from typing import List
import structlog

from app.ai.swarm.dependency_resolver import DependencyResolver
from app.ai.swarm.models import SwarmMissionGraph, SwarmTask
from app.ai.swarm.parallel_executor import ParallelExecutor

logger = structlog.get_logger("execution_coordinator")


class ExecutionCoordinator:
    """Coordinates wave-by-wave parallel execution of task DAGs."""

    def __init__(self, executor: ParallelExecutor) -> None:
        self.executor = executor
        self.resolver = DependencyResolver()

    async def coordinate_execution(self, graph: SwarmMissionGraph) -> List[SwarmTask]:
        """Coordinate parallel wave execution of all tasks in graph."""
        waves = self.resolver.resolve_execution_waves(graph)
        executed_tasks: List[SwarmTask] = []
        for i, wave in enumerate(waves, 1):
            logger.info("Coordinating execution wave", wave_number=i, tasks_count=len(wave))
            res = await self.executor.execute_task_wave(wave)
            executed_tasks.extend(res)

        return executed_tasks
