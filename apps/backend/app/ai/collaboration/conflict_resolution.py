"""Conflict Resolution helper resolving duplicate task allocations and incompatible outputs.
"""

import structlog
from typing import Dict, Any, List

logger = structlog.get_logger("conflict_resolution")

class ConflictResolver:
    """Manages circular logic detection and duplicates task ownership arbitration."""

    def resolve_duplicate_ownership(self, agent_a: str, agent_b: str, capability: str) -> str:
        """Resolves task ownership to the agent with better semantic name alignment."""
        logger.info("Resolving duplicate task allocation conflict", agent_a=agent_a, agent_b=agent_b, capability=capability)
        # Prioritize specialty matches
        if capability in agent_a:
            return agent_a
        return agent_b

    def resolve_conflicting_outputs(self, architect_opinion: Dict[str, Any], developer_opinion: Dict[str, Any]) -> Dict[str, Any]:
        """Resolves output structure conflicts by merging and prioritizing Architect opinions."""
        logger.info("Merging conflicting opinions outputs")
        merged = {**developer_opinion, **architect_opinion}
        return merged
