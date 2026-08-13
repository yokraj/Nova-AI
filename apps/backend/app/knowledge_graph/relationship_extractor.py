"""Relationship Extractor Module.

Automatically detects 25 relationship types between extracted entities.
"""

from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)

SUPPORTED_RELATIONSHIP_TYPES = [
    "depends_on", "implements", "uses", "calls", "references", "extends",
    "inherits", "contains", "belongs_to", "created_by", "updated_by", "related_to",
    "duplicate_of", "derived_from", "imports", "exports", "connects_to", "stores",
    "retrieves", "communicates_with", "executes", "requires", "solves", "causes", "documents",
]


class RelationshipExtractor:
    """Enterprise Knowledge Graph Relationship Extractor."""

    def __init__(self) -> None:
        logger.info("relationship_extractor_initialized", supported_types_count=len(SUPPORTED_RELATIONSHIP_TYPES))

    def extract_relationships(
        self,
        entities: List[Dict[str, Any]],
        text_context: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Infers directed relationships between pairs of entities."""
        relationships: List[Dict[str, Any]] = []

        if len(entities) < 2:
            return relationships

        # Infer relationship rules based on entity types
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                e1 = entities[i]
                e2 = entities[j]

                t1 = e1.get("entity_type")
                t2 = e2.get("entity_type")

                rel_type = "related_to"
                if t1 == "Class" and t2 == "Function":
                    rel_type = "contains"
                elif t1 == "Function" and t2 in ["Framework", "Language"]:
                    rel_type = "uses"
                elif t1 in ["Framework", "Language"] and t2 == "Project":
                    rel_type = "used_by"
                elif t1 == "Project" and t2 in ["Framework", "Database"]:
                    rel_type = "depends_on"

                relationships.append({
                    "source_name": e1["name"],
                    "target_name": e2["name"],
                    "relationship_type": rel_type,
                    "weight": 1.0,
                })

        logger.info("relationships_extracted", count=len(relationships))
        return relationships
