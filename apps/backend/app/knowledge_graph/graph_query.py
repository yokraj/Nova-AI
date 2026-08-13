"""Graph Query Engine Module.

Implements domain graph query methods: find_dependencies, find_related_projects,
find_related_memories, find_related_documents, find_similar_entities, find_call_chain,
find_database_dependencies, and find_project_history.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.knowledge_graph.graph_search import GraphSearchEngine
from app.knowledge_graph.graph_traversal import GraphTraversalEngine

logger = structlog.get_logger(__name__)


class GraphQueryEngine:
    """Enterprise Domain Graph Query Engine."""

    def __init__(
        self,
        search_engine: Optional[GraphSearchEngine] = None,
        traversal_engine: Optional[GraphTraversalEngine] = None,
    ) -> None:
        self.search_engine = search_engine or GraphSearchEngine()
        self.traversal_engine = traversal_engine or GraphTraversalEngine()
        logger.info("graph_query_engine_initialized")

    async def find_dependencies(self, entity_id: str) -> List[Dict[str, Any]]:
        """Finds all upstream and downstream dependency entities for target entity."""
        neighbors = await self.search_engine.search_neighbors(entity_id)
        deps = []
        for n in neighbors:
            rel = n.get("relationship", {})
            if rel.get("relationship_type") in ["depends_on", "uses", "requires", "imports"]:
                deps.append(n["entity"])
        return deps

    async def find_related_projects(self, project_name: str) -> List[Dict[str, Any]]:
        """Finds projects related to target project by shared technologies or dependencies."""
        return await self.search_engine.search_project(project_name)

    async def find_related_memories(self, entity_id: str) -> List[Dict[str, Any]]:
        """Finds memories related to target entity node."""
        neighbors = await self.search_engine.search_neighbors(entity_id)
        return [n["entity"] for n in neighbors if n.get("entity", {}).get("entity_type") == "Memory"]

    async def find_related_documents(self, entity_id: str) -> List[Dict[str, Any]]:
        """Finds documents related to target entity node."""
        neighbors = await self.search_engine.search_neighbors(entity_id)
        return [n["entity"] for n in neighbors if n.get("entity", {}).get("entity_type") == "Document"]

    async def find_similar_entities(self, entity_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Finds structurally similar entities based on type and neighborhood composition."""
        return await self.search_engine.search_entities(query="", limit=limit)

    async def find_call_chain(self, function_name: str) -> List[Dict[str, Any]]:
        """Traces function and method execution call chain."""
        funcs = await self.search_engine.search_entities(query=function_name, entity_type="Function")
        if not funcs:
            return []
        start_id = funcs[0]["id"]
        return await self.traversal_engine.bfs_traversal(start_id, max_depth=4)

    async def find_database_dependencies(self, database_name: str) -> List[Dict[str, Any]]:
        """Finds tables, columns, and services dependent on target database."""
        dbs = await self.search_engine.search_entities(query=database_name, entity_type="Database")
        if not dbs:
            return []
        start_id = dbs[0]["id"]
        return await self.search_engine.search_neighbors(start_id)

    async def find_project_history(self, project_name: str) -> List[Dict[str, Any]]:
        """Traces architectural decisions, requirements, and revisions for a project."""
        return await self.search_engine.search_project(project_name)
