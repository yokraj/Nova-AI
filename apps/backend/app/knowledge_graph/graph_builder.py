"""Graph Builder Module.

Automates Knowledge Graph construction, incremental entity/relationship insertion,
batch rebuilds, synchronization, and version tracking.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.knowledge_graph.config import KnowledgeGraphConfig
from app.knowledge_graph.entity_extractor import EntityExtractor
from app.knowledge_graph.relationship_extractor import RelationshipExtractor
from app.knowledge_graph.graph_storage import GraphStorage

logger = structlog.get_logger(__name__)


class GraphBuilder:
    """Enterprise Automated Knowledge Graph Construction Engine."""

    def __init__(
        self,
        config: Optional[KnowledgeGraphConfig] = None,
        storage: Optional[GraphStorage] = None,
        entity_extractor: Optional[EntityExtractor] = None,
        relationship_extractor: Optional[RelationshipExtractor] = None,
    ) -> None:
        self.config = config or KnowledgeGraphConfig()
        self.storage = storage or GraphStorage(config=self.config)
        self.entity_extractor = entity_extractor or EntityExtractor()
        self.relationship_extractor = relationship_extractor or RelationshipExtractor()
        self.version = 1
        logger.info("graph_builder_initialized", version=self.version)

    async def ingest_content(
        self, text: str, workspace: str = "Nova", project: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ingests text content, extracts entity nodes and relationship edges, and updates graph."""
        entities = self.entity_extractor.extract_entities_from_text(text, workspace=workspace, project=project)
        relationships = self.relationship_extractor.extract_relationships(entities, text_context=text)

        added_entities: List[str] = []
        name_to_id: Dict[str, str] = {}

        for ent in entities:
            ent_id = await self.storage.driver.add_entity(ent)
            added_entities.append(ent_id)
            name_to_id[ent["name"]] = ent_id

        added_relationships: List[str] = []
        for rel in relationships:
            src_id = name_to_id.get(rel["source_name"])
            tgt_id = name_to_id.get(rel["target_name"])
            if src_id and tgt_id:
                rel_data = dict(rel)
                rel_data["source_id"] = src_id
                rel_data["target_id"] = tgt_id
                rel_data["workspace"] = workspace
                rel_data["project"] = project
                rel_id = await self.storage.driver.add_relationship(rel_data)
                added_relationships.append(rel_id)

        logger.info("content_ingested_into_graph", entity_count=len(added_entities), rel_count=len(added_relationships))
        return {
            "entities_added": len(added_entities),
            "relationships_added": len(added_relationships),
            "graph_version": self.version,
        }

    async def batch_rebuild(self, text_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Performs full batch graph rebuild across items."""
        self.version += 1
        total_entities = 0
        total_rels = 0

        for item in text_items:
            res = await self.ingest_content(
                text=item.get("content", ""),
                workspace=item.get("workspace", "Nova"),
                project=item.get("project"),
            )
            total_entities += res["entities_added"]
            total_rels += res["relationships_added"]

        logger.info("batch_graph_rebuild_completed", version=self.version)
        return {
            "status": "rebuilt",
            "version": self.version,
            "total_entities": total_entities,
            "total_relationships": total_rels,
        }
