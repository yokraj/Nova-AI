"""Agent Allocator binding task execution to allocated agents."""

from typing import Optional
import structlog

from app.ai.swarm.agent_registry import AgentRegistry
from app.ai.swarm.agent_selector import AgentSelector
from app.ai.swarm.capability_matcher import CapabilityMatcher
from app.ai.swarm.interfaces import ILoadBalancer
from app.ai.swarm.models import SwarmAgentRecord, SwarmTask

logger = structlog.get_logger("agent_allocator")


class AgentAllocator(ILoadBalancer):
    """Allocates idle agents to tasks based on capability matching and workload."""

    def __init__(self, registry: Optional[AgentRegistry] = None) -> None:
        self.registry = registry or AgentRegistry()
        self.matcher = CapabilityMatcher(registry=self.registry)
        self.selector = AgentSelector()

    async def allocate_task(self, task: SwarmTask) -> SwarmAgentRecord:
        """Allocate agent to task."""
        candidates = self.matcher.match_task(task)
        selected = self.selector.select_best_agent(candidates)
        selected.is_busy = True
        task.assigned_agent_id = selected.agent_id
        logger.info("Allocated agent to task", task_id=task.task_id, agent_id=selected.agent_id, agent_name=selected.name)
        return selected
