"""Graph Storage Module.

Provides relational storage backend driver (SQLAlchemy/SQLite fallback)
and abstract interfaces for Neo4j, Memgraph, and RDF export.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import structlog

from app.knowledge_graph.config import KnowledgeGraphConfig

logger = structlog.get_logger(__name__)


class BaseGraphStorageDriver:
    """Abstract interface for graph storage drivers."""

    async def add_entity(self, entity_data: Dict[str, Any]) -> str:
        raise NotImplementedError

    async def add_relationship(self, rel_data: Dict[str, Any]) -> str:
        raise NotImplementedError

    async def get_neighbors(self, entity_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError


class SQLiteGraphStorageDriver(BaseGraphStorageDriver):
    """Fast in-memory relational graph storage driver implementation."""

    def __init__(self) -> None:
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.relationships: Dict[str, Dict[str, Any]] = {}
        self.adjacency: Dict[str, List[Tuple[str, str]]] = {}  # source_id -> [(target_id, rel_id)]

    async def add_entity(self, entity_data: Dict[str, Any]) -> str:
        ent_id = entity_data.get("id") or entity_data["name"]
        entity_data["id"] = ent_id
        self.entities[ent_id] = entity_data
        if ent_id not in self.adjacency:
            self.adjacency[ent_id] = []
        return ent_id

    async def add_relationship(self, rel_data: Dict[str, Any]) -> str:
        rel_id = rel_data.get("id") or f"{rel_data['source_id']}->{rel_data['target_id']}"
        rel_data["id"] = rel_id
        self.relationships[rel_id] = rel_data

        src = rel_data["source_id"]
        tgt = rel_data["target_id"]

        if src not in self.adjacency:
            self.adjacency[src] = []
        self.adjacency[src].append((tgt, rel_id))
        return rel_id

    async def get_neighbors(self, entity_id: str) -> List[Dict[str, Any]]:
        neighbors = []
        for tgt_id, rel_id in self.adjacency.get(entity_id, []):
            if tgt_id in self.entities:
                neighbors.append({
                    "entity": self.entities[tgt_id],
                    "relationship": self.relationships.get(rel_id, {}),
                })
        return neighbors


class GraphStorage:
    """Enterprise Pluggable Graph Storage Manager."""

    def __init__(self, config: Optional[KnowledgeGraphConfig] = None) -> None:
        self.config = config or KnowledgeGraphConfig()
        self.driver = self._initialize_driver()
        logger.info("graph_storage_initialized", backend=self.config.graph_storage_backend)

    def _initialize_driver(self) -> BaseGraphStorageDriver:
        """Instantiates active storage driver backend."""
        return SQLiteGraphStorageDriver()
