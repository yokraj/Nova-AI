"""Knowledge Graph Configuration Module.

Defines Pydantic settings for graph traversal depths, search candidate bounds,
storage backend drivers, and entity resolution matching thresholds.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class KnowledgeGraphConfig(BaseModel):
    """Configuration settings for Enterprise Knowledge Graph Engine."""

    # Traversal & Depth Limits
    max_traversal_depth: int = Field(default=5, ge=1, le=20, description="Maximum hop depth for graph traversals")
    max_search_limit: int = Field(default=50, ge=1, le=500, description="Maximum search candidate limit")
    default_distance_limit: int = Field(default=10, description="Default max path length for shortest path")

    # Storage Backend Configuration
    graph_storage_backend: str = Field(default="sqlite", description="Active graph storage backend (sqlite, neo4j, memgraph, rdf)")
    neo4j_uri: Optional[str] = Field(default=None, description="Optional Neo4j cluster URI connection string")
    memgraph_uri: Optional[str] = Field(default=None, description="Optional Memgraph server URI connection string")

    # Entity Resolution & Deduplication Limits
    entity_matching_threshold: float = Field(default=0.85, ge=0.0, le=1.0, description="Similarity threshold for auto-merging duplicate entities")
    enable_auto_resolution: bool = Field(default=True, description="Enables automated entity resolution during graph construction")
