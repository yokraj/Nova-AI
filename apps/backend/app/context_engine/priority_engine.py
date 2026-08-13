"""Priority Engine Module.

Assigns priority tiers (Critical, High, Medium, Low) to context sections
to govern token budget allocation.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class PriorityEngine:
    """Enterprise Context Priority Tier Assignment Engine."""

    def __init__(self) -> None:
        logger.info("priority_engine_initialized")

    def assign_priorities(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Categorizes candidates into priority levels (Critical, High, Medium, Low)."""
        prioritized = []
        for item in candidates:
            score = item.get("fused_score", item.get("confidence", 0.5))
            if score >= 0.85:
                tier = "Critical"
            elif score >= 0.70:
                tier = "High"
            elif score >= 0.50:
                tier = "Medium"
            else:
                tier = "Low"

            item_copy = dict(item)
            item_copy["priority_tier"] = tier
            prioritized.append(item_copy)

        return prioritized
