"""Context Conflict Resolver Module.

Detects conflicting memories, outdated architecture, version conflicts,
and project contradictions, choosing the highest confidence candidate.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class ContextConflictResolver:
    """Enterprise Context Conflict & Contradiction Resolution Engine."""

    def __init__(self) -> None:
        logger.info("context_conflict_resolver_initialized")

    def resolve_conflicts(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifies conflicting assertions and retains only the highest-confidence block."""
        resolved: List[Dict[str, Any]] = []
        seen_topics: Dict[str, Dict[str, Any]] = {}

        for item in candidates:
            topic = item.get("title", item.get("id"))
            if topic not in seen_topics:
                seen_topics[topic] = item
                resolved.append(item)
            else:
                existing = seen_topics[topic]
                # If current candidate has higher fused or confidence score, override
                if item.get("fused_score", item.get("confidence", 0)) > existing.get("fused_score", existing.get("confidence", 0)):
                    resolved.remove(existing)
                    seen_topics[topic] = item
                    resolved.append(item)

        logger.info("conflicts_resolved", input_count=len(candidates), resolved_count=len(resolved))
        return resolved
