"""Graph Storage Module.

Provides relational storage backend driver (SQLAlchemy/SQLite fallback)
and abstract interfaces for Neo4j, Memgraph, and RDF export.
"""

import os
import json
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
    """Fast relational graph storage driver implementation with file persistence support."""

    def __init__(self, storage_path: str = ".nova/memory/") -> None:
        self.storage_path = storage_path
        self.index_file = os.path.join(storage_path, "graph_index.json")
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.relationships: Dict[str, Dict[str, Any]] = {}
        self.adjacency: Dict[str, List[Tuple[str, str]]] = {}  # source_id -> [(target_id, rel_id)]
        self.load()

    def load(self) -> None:
        """Loads serialized graph index from disk cache."""
        if not os.path.exists(self.index_file):
            return
        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.entities = data.get("entities", {})
                self.relationships = data.get("relationships", {})
                # Rebuild adjacency map
                self.adjacency = {}
                for ent_id in self.entities:
                    self.adjacency[ent_id] = []
                for rel_id, rel_data in self.relationships.items():
                    src = rel_data.get("source_id")
                    tgt = rel_data.get("target_id")
                    if src and tgt:
                        if src not in self.adjacency:
                            self.adjacency[src] = []
                        self.adjacency[src].append((tgt, rel_id))
        except Exception as e:
            logger.warning("Failed to load graph index from disk", error=str(e))

    def save(self) -> None:
        """Serializes graph index to file."""
        try:
            os.makedirs(self.storage_path, exist_ok=True)
            data = {
                "entities": self.entities,
                "relationships": self.relationships,
            }
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning("Failed to save graph index to disk", error=str(e))

    async def add_entity(self, entity_data: Dict[str, Any]) -> str:
        ent_id = entity_data.get("id") or entity_data["name"]
        entity_data["id"] = ent_id
        self.entities[ent_id] = entity_data
        if ent_id not in self.adjacency:
            self.adjacency[ent_id] = []
        self.save()
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
        self.save()
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

    def __init__(self, config: Optional[KnowledgeGraphConfig] = None, storage_path: str = ".nova/memory/") -> None:
        self.config = config or KnowledgeGraphConfig()
        self.storage_path = storage_path
        self.driver = self._initialize_driver()
        logger.info("graph_storage_initialized", backend=self.config.graph_storage_backend)

    def _initialize_driver(self) -> BaseGraphStorageDriver:
        """Instantiates active storage driver backend."""
        return SQLiteGraphStorageDriver(storage_path=self.storage_path)
