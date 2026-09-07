"""Knowledge Graph Engine Master Orchestrator Module.

Integrates Universal Intelligence Engine, Memory Engine, Vector Memory, Hybrid RAG Engine,
Conversation Engine, Decision Engine, Project Memory, and Workspace Memory.
"""

from typing import Any, Dict, List, Optional
import structlog

from sqlalchemy.ext.asyncio import AsyncSession

from app.knowledge_graph.config import KnowledgeGraphConfig
from app.knowledge_graph.repository import KnowledgeGraphRepository
from app.knowledge_graph.service import (
    KnowledgeGraphService,
    EntityService,
    RelationshipService,
    GraphQueryService,
    ReasoningService,
)

from app.knowledge_graph.graph_storage import GraphStorage
from app.knowledge_graph.graph_search import GraphSearchEngine

logger = structlog.get_logger(__name__)


class KnowledgeGraphEngine:
    """Enterprise Master Knowledge Graph Engine Orchestrator."""

    def __init__(
        self,
        session: Optional[AsyncSession] = None,
        config: Optional[KnowledgeGraphConfig] = None,
        storage: Optional[GraphStorage] = None,
        storage_path: str = ".nova/memory/",
    ) -> None:
        self.session = session
        self.config = config or KnowledgeGraphConfig()
        self.storage = storage or GraphStorage(config=self.config, storage_path=storage_path)
        self.repository = KnowledgeGraphRepository(session=session)
        self.search_engine = GraphSearchEngine(storage=self.storage)

        # Services Initialization
        self.graph_service = KnowledgeGraphService(repository=self.repository)
        self.entity_service = EntityService(repository=self.repository)
        self.relationship_service = RelationshipService(repository=self.repository)
        self.query_service = GraphQueryService(repository=self.repository)
        self.reasoning_service = ReasoningService(repository=self.repository)

        logger.info("knowledge_graph_engine_master_initialized")

    async def query_relevant_graph(self, query: str) -> str:
        """Queries graph for entities and relationships matching terms in query string."""
        if not self.storage or not hasattr(self.storage, "driver"):
            return ""

        driver = self.storage.driver
        if not hasattr(driver, "entities") or not driver.entities:
            return ""

        q_lower = query.lower()
        matched_entities: Dict[str, Dict[str, Any]] = {}
        matched_relationships: Dict[str, Dict[str, Any]] = {}

        stopwords = {"what", "is", "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "my", "i", "am", "do", "does", "did", "how", "using"}
        tokens = [t.strip("?,.!") for t in q_lower.split() if t.strip("?,.!") and t.strip("?,.!") not in stopwords]

        # 1. Match seed entities by name or entity_type
        for ent_id, ent in driver.entities.items():
            name_lower = ent.get("name", "").lower()
            type_lower = ent.get("entity_type", "").lower()

            if any(t in name_lower or name_lower in t or t in type_lower for t in tokens):
                matched_entities[ent_id] = ent

        if not matched_entities:
            return ""

        # 2. Collect 1-hop neighbor connections for matched seed entities
        for ent_id in list(matched_entities.keys()):
            neighbors = await driver.get_neighbors(ent_id)
            for n in neighbors:
                tgt_ent = n.get("entity")
                rel = n.get("relationship")
                if tgt_ent:
                    matched_entities[tgt_ent["id"]] = tgt_ent
                if rel:
                    matched_relationships[rel["id"]] = rel

        # 3. Collect relationships referencing any matched entities
        if hasattr(driver, "relationships"):
            for rel_id, rel in driver.relationships.items():
                src_id = rel.get("source_id")
                tgt_id = rel.get("target_id")
                if src_id in matched_entities or tgt_id in matched_entities:
                    matched_relationships[rel_id] = rel
                    if src_id in driver.entities:
                        matched_entities[src_id] = driver.entities[src_id]
                    if tgt_id in driver.entities:
                        matched_entities[tgt_id] = driver.entities[tgt_id]

        if not matched_entities and not matched_relationships:
            return ""

        # 4. Format into clean output string
        entity_lines = []
        for ent in matched_entities.values():
            e_name = ent.get("name")
            e_type = ent.get("entity_type", "Entity")
            entity_lines.append(f"- {e_name} (Type: {e_type})")

        rel_lines = []
        for rel in matched_relationships.values():
            src_id = rel.get("source_id")
            tgt_id = rel.get("target_id")
            r_type = rel.get("relationship_type", "related_to")

            src_name = driver.entities.get(src_id, {}).get("name", src_id)
            tgt_name = driver.entities.get(tgt_id, {}).get("name", tgt_id)

            rel_lines.append(f"- {src_name} --[{r_type}]--> {tgt_name}")

        parts = []
        if entity_lines:
            parts.append("Entities:\n" + "\n".join(entity_lines))
        if rel_lines:
            parts.append("Relationships:\n" + "\n".join(rel_lines))

        return "\n\n".join(parts)
