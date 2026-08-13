"""Graph Search Module.

Implements search_entities, search_relationships, search_neighbors, search_paths,
search_by_type, search_workspace, and search_project.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.knowledge_graph.graph_storage import GraphStorage, SQLiteGraphStorageDriver

logger = structlog.get_logger(__name__)


class GraphSearchEngine:
    """Enterprise Knowledge Graph Search Engine."""

    def __init__(self, storage: Optional[GraphStorage] = None) -> None:
        self.storage = storage or GraphStorage()
        logger.info("graph_search_engine_initialized")

    async def search_entities(
        self, query: str, entity_type: Optional[str] = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Searches graph entity nodes by substring query or entity type."""
        driver = self.storage.driver
        if not isinstance(driver, SQLiteGraphStorageDriver):
            return []

        results = []
        q_lower = query.lower()

        for ent in driver.entities.values():
            name_match = q_lower in ent["name"].lower()
            type_match = True if not entity_type else ent.get("entity_type") == entity_type
            if name_match and type_match:
                results.append(ent)
                if len(results) >= limit:
                    break

        logger.info("entities_searched", query=query, count=len(results))
        return results

    async def search_relationships(
        self, relationship_type: Optional[str] = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Searches graph relationship edges by type."""
        driver = self.storage.driver
        if not isinstance(driver, SQLiteGraphStorageDriver):
            return []

        results = []
        for rel in driver.relationships.values():
            if not relationship_type or rel.get("relationship_type") == relationship_type:
                results.append(rel)
                if len(results) >= limit:
                    break

        return results

    async def search_neighbors(self, entity_id: str) -> List[Dict[str, Any]]:
        """Finds immediate candidate neighbors connected to entity_id."""
        return await self.storage.driver.get_neighbors(entity_id)

    async def search_by_type(self, entity_type: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Queries entities filtered by entity type."""
        return await self.search_entities(query="", entity_type=entity_type, limit=limit)

    async def search_workspace(self, workspace: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Queries entities filtered by workspace scope."""
        driver = self.storage.driver
        if not isinstance(driver, SQLiteGraphStorageDriver):
            return []
        return [e for e in driver.entities.values() if e.get("workspace") == workspace][:limit]

    async def search_project(self, project: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Queries entities filtered by project scope."""
        driver = self.storage.driver
        if not isinstance(driver, SQLiteGraphStorageDriver):
            return []
        return [e for e in driver.entities.values() if e.get("project") == project][:limit]
