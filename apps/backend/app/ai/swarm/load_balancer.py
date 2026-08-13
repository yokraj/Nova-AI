"""Load Balancer managing agent workload and task reassignment on failure."""

from typing import List, Optional
import structlog

from app.ai.swarm.agent_allocator import AgentAllocator
from app.ai.swarm.models import SwarmAgentRecord, SwarmTask

logger = structlog.get_logger("load_balancer")


class LoadBalancer:
    """Tracks agent workload, busy/idle states, and handles task reassignment upon agent failure."""

    def __init__(self, allocator: Optional[AgentAllocator] = None) -> None:
        self.allocator = allocator or AgentAllocator()

    async def reassign_failed_task(self, task: SwarmTask, failed_agent_id: str) -> SwarmAgentRecord:
        """Reassign failed task to another agent."""
        logger.warning("Reassigning failed task to alternative agent", task_id=task.task_id, failed_agent=failed_agent_id)
        new_agent = await self.allocator.allocate_task(task)
        return new_agent
