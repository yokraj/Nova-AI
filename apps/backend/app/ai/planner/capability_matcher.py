"""Capability Matcher mapping task requirements to registered capabilities.
"""

import structlog
from typing import List, Dict, Any, Optional
from app.ai.planner.models import Task

logger = structlog.get_logger("capability_matcher")

class CapabilityMatcher:
    """Discovers matching capabilities from active AgentRegistries."""

    def __init__(self, registry: Optional[Any] = None) -> None:
        self.registry = registry

    def find_matches(self, task: Task) -> List[Dict[str, Any]]:
        """Queries registrants possessing matching capability identifiers."""
        matches = []
        if not self.registry:
            return matches

        for requirement in task.required_capabilities:
            for registration in self.registry.list():
                for capability in registration.metadata.capabilities:
                    if capability.name.lower() == requirement.capability_name.lower():
                        matches.append({
                            "agent_id": registration.metadata.id,
                            "agent_name": registration.metadata.name,
                            "capability_score": 0.85,
                            "permissions": registration.metadata.permissions
                        })

        logger.debug("Query resolved capability matches", task_id=task.task_id, matches_count=len(matches))
        return matches
