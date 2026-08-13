"""Negotiation Engine managing task ownership bids among specialized agents.
"""

import structlog
from typing import List, Dict, Any
from app.ai.collaboration.models import NegotiationBid
from app.ai.collaboration.interfaces import INegotiationEngine
from app.core.dependency_container import resolve
from app.ai.gateway import IAIGateway

logger = structlog.get_logger("negotiation_engine")

class NegotiationEngine(INegotiationEngine):
    """Enables agents to bid for tasks based on workload and capability score match ratios."""

    def __init__(self, registry: Any = None) -> None:
        self._registry = registry

    @property
    def registry(self) -> Any:
        if self._registry is None:
            try:
                gateway = resolve(IAIGateway)
                self._registry = gateway.agents.registry
            except Exception:
                pass
        return self._registry

    async def negotiate_ownership(self, task_id: str, capabilities: List[str]) -> str:
        """Invokes capability scoring rules to balance workload ownership assignees."""
        logger.info("Initiated ownership negotiation round", task_id=task_id, capabilities=capabilities)
        if not self.registry:
            return "software_engineer"

        bids: List[NegotiationBid] = []
        for reg in self.registry.list():
            agent_id = reg.metadata.id
            metadata = reg.metadata
            if not metadata:
                continue

            agent_caps = {cap.name for cap in metadata.capabilities}
            matching = agent_caps.intersection(set(capabilities))
            if not matching and capabilities:
                continue

            cap_score = len(matching) / len(capabilities) if capabilities else 0.5
            # Workload balancing (default simulated available factor)
            workload_score = 0.9

            bid_value = (cap_score * 0.7) + (workload_score * 0.3)
            bids.append(NegotiationBid(
                agent_id=agent_id,
                capability_score=cap_score,
                workload_score=workload_score,
                bid_value=bid_value
            ))

        if not bids:
            logger.warn("Negotiation found no qualified bidders. Defaulting task ownership fallback.", task_id=task_id)
            return "software_engineer"

        bids.sort(key=lambda b: b.bid_value, reverse=True)
        winner = bids[0].agent_id
        logger.info("Negotiation bid won", task_id=task_id, winner=winner, bid_value=bids[0].bid_value)
        return winner
