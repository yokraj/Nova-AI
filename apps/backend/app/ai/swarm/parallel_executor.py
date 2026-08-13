"""Parallel Executor running ready task nodes concurrently across allocated agents."""

import asyncio
from typing import Any, Dict, List
import structlog

from app.ai.swarm.agent_allocator import AgentAllocator
from app.ai.swarm.models import SwarmTask, TaskState

logger = structlog.get_logger("parallel_executor")


class ParallelExecutor:
    """Executes independent tasks concurrently using async asyncio.gather workers."""

    def __init__(self, allocator: AgentAllocator) -> None:
        self.allocator = allocator

    async def execute_task_wave(self, tasks: List[SwarmTask]) -> List[SwarmTask]:
        """Execute a wave of independent tasks in parallel."""
        logger.info("Executing task wave concurrently", count=len(tasks))

        async def _worker(t: SwarmTask) -> SwarmTask:
            t.state = TaskState.RUNNING
            agent = await self.allocator.allocate_task(t)
            await asyncio.sleep(0.05)  # Concurrent simulation
            t.output_data = {
                "result": f"Task '{t.title}' executed successfully by {agent.name}",
                "agent_id": agent.agent_id,
                "status": "success",
            }
            t.state = TaskState.COMPLETED
            agent.is_busy = False
            agent.completed_tasks_count += 1
            logger.info("Completed swarm task", task_id=t.task_id, title=t.title, agent=agent.name)
            return t

        return list(await asyncio.gather(*[_worker(t) for t in tasks]))
