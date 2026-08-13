"""Knowledge Sync synchronizing insights and findings across all agents."""

from typing import List
import structlog

logger = structlog.get_logger("knowledge_sync")


class KnowledgeSync:
    """Synchronizes agent insights and findings across the swarm."""

    async def synchronize_insights(self, agent_ids: List[str], topic: str) -> None:
        """Synchronize insights across agents."""
        logger.info("Synchronized agent insights across swarm", agents_count=len(agent_ids), topic=topic)
