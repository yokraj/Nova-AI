"""Entity Resolution Module.

Implements entity deduplication, alias resolution, and string/version normalization.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.knowledge_graph.config import KnowledgeGraphConfig

logger = structlog.get_logger(__name__)


class EntityResolver:
    """Enterprise Entity Resolution & Deduplication Engine."""

    def __init__(self, config: Optional[KnowledgeGraphConfig] = None) -> None:
        self.config = config or KnowledgeGraphConfig()
        logger.info("entity_resolver_initialized")

    def normalize_name(self, name: str) -> str:
        """Normalizes entity name strings."""
        return name.strip().lower().replace("-", "_").replace(" ", "_")

    def resolve_duplicates(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merges duplicate entity nodes based on normalized name and entity type matching."""
        resolved_map: Dict[str, Dict[str, Any]] = {}

        for ent in entities:
            norm_key = f"{ent.get('entity_type', 'Memory')}:{self.normalize_name(ent['name'])}"
            if norm_key not in resolved_map:
                ent_copy = dict(ent)
                ent_copy["aliases"] = ent_copy.get("aliases", [])
                resolved_map[norm_key] = ent_copy
            else:
                existing = resolved_map[norm_key]
                existing["aliases"].append(ent["name"])
                if ent.get("description") and not existing.get("description"):
                    existing["description"] = ent["description"]

        merged_list = list(resolved_map.values())
        logger.info("entities_resolved", original_count=len(entities), resolved_count=len(merged_list))
        return merged_list
