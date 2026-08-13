"""Knowledge Graph Schemas Module.

Defines Pydantic DTO request/response schemas for graph entities, relationships,
traversals, reasoning queries, visualizations, health diagnostics, and telemetry statistics.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class EntityCreateRequest(BaseModel):
    """Request schema for creating or indexing a graph entity node."""

    name: str = Field(min_length=1, description="Entity name identifier")
    entity_type: str = Field(description="Entity type (User, Project, Memory, CodeFile, Function, API, etc.)")
    description: Optional[str] = Field(default=None)
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict)
    aliases: Optional[List[str]] = Field(default_factory=list)
    workspace: str = Field(default="Nova")
    project: Optional[str] = Field(default=None)


class EntityResponse(BaseModel):
    """Response DTO for graph entity node."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    entity_type: str
    description: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)
    aliases: List[str] = Field(default_factory=list)
    workspace: str
    project: Optional[str] = None
    created_at: datetime


class RelationshipCreateRequest(BaseModel):
    """Request schema for creating a graph relationship edge."""

    source_id: str = Field(description="Source entity UUID")
    target_id: str = Field(description="Target entity UUID")
    relationship_type: str = Field(description="Relationship edge type (depends_on, implements, uses, etc.)")
    weight: float = Field(default=1.0, ge=0.0)
    attributes: Optional[Dict[str, Any]] = Field(default_factory=dict)
    workspace: str = Field(default="Nova")
    project: Optional[str] = Field(default=None)


class RelationshipResponse(BaseModel):
    """Response DTO for graph relationship edge."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    source_id: str
    target_id: str
    relationship_type: str
    weight: float
    attributes: Dict[str, Any] = Field(default_factory=dict)
    workspace: str
    project: Optional[str] = None
    created_at: datetime


class GraphPathResponse(BaseModel):
    """Response DTO for graph traversal path."""

    start_entity_id: str
    end_entity_id: str
    path_nodes: List[Dict[str, Any]]
    path_edges: List[Dict[str, Any]]
    hop_count: int
    total_weight: float


class GraphVisualizationResponse(BaseModel):
    """Response DTO for rendered graph visualizations."""

    mermaid_code: str
    json_graph: Dict[str, Any]
    node_count: int
    edge_count: int


class GraphHealthResponse(BaseModel):
    """Health diagnostic report for knowledge graph engine."""

    status: str = "healthy"
    integrity_valid: bool = True
    no_orphans: bool = True
    no_cycles: bool = True
    details: Dict[str, Any] = Field(default_factory=dict)


class GraphStatisticsResponse(BaseModel):
    """Telemetry metrics summary for knowledge graph."""

    model_config = ConfigDict(from_attributes=True)

    entity_count: int
    relationship_count: int
    graph_density: float
    connected_components: int
    average_degree: float
    query_latency: float
    traversal_latency: float
    storage_usage: int
    timestamp: datetime
