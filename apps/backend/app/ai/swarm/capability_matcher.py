"""Capability Matcher matching required task capabilities with agent roles."""

from typing import List, Optional
import structlog

from app.ai.swarm.agent_registry import AgentRegistry
from app.ai.swarm.models import AgentRole, SwarmAgentRecord, SwarmTask

logger = structlog.get_logger("capability_matcher")


class CapabilityMatcher:
    """Matches decomposed tasks with agent roles and capabilities."""

    def __init__(self, registry: Optional[AgentRegistry] = None) -> None:
        self.registry = registry or AgentRegistry()

    def match_task(self, task: SwarmTask) -> List[SwarmAgentRecord]:
        """Find candidate agents for task."""
        candidates = self.registry.find_agents_by_role(task.required_role.value)
        if not candidates:
            candidates = self.registry.list_all_agents()
        logger.debug("Matched candidates for task", task_id=task.task_id, candidates_count=len(candidates))
        return candidates
