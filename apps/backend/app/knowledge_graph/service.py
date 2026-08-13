"""Knowledge Graph Service Layer Module.

Provides decoupled asynchronous business service abstractions:
KnowledgeGraphService, EntityService, RelationshipService, GraphQueryService, and ReasoningService.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.knowledge_graph.repository import KnowledgeGraphRepository
from app.knowledge_graph.graph_builder import GraphBuilder
from app.knowledge_graph.graph_search import GraphSearchEngine
from app.knowledge_graph.graph_traversal import GraphTraversalEngine
from app.knowledge_graph.graph_query import GraphQueryEngine
from app.knowledge_graph.graph_reasoner import GraphReasoner
from app.knowledge_graph.graph_visualization import GraphVisualizer
from app.knowledge_graph.graph_statistics import GraphStatisticsTracker
from app.knowledge_graph.health import GraphHealthChecker
from app.knowledge_graph.schemas import (
    EntityCreateRequest,
    EntityResponse,
    RelationshipCreateRequest,
    RelationshipResponse,
    GraphPathResponse,
    GraphVisualizationResponse,
    GraphHealthResponse,
    GraphStatisticsResponse,
)

logger = structlog.get_logger(__name__)


class EntityService:
    """Business service handling entity node operations."""

    def __init__(self, repository: KnowledgeGraphRepository) -> None:
        self.repository = repository
        self.search_engine = GraphSearchEngine()
        logger.info("entity_service_initialized")

    async def create_entity(self, request: EntityCreateRequest) -> EntityResponse:
        """Creates and persists a graph entity node."""
        record = await self.repository.save_entity(
            name=request.name,
            entity_type=request.entity_type,
            description=request.description,
            attributes=request.attributes,
            aliases=request.aliases,
            workspace=request.workspace,
            project=request.project,
        )

        return EntityResponse(
            id=record.id,
            name=record.name,
            entity_type=record.entity_type,
            description=record.description,
            attributes=record.attributes if isinstance(record.attributes, dict) else {},
            aliases=record.aliases if isinstance(record.aliases, list) else [],
            workspace=record.workspace,
            project=record.project,
            created_at=record.created_at,
        )

    async def get_entity(self, entity_id: str) -> Optional[EntityResponse]:
        """Fetches entity node by ID."""
        record = await self.repository.get_entity(entity_id)
        if not record:
            return None
        return EntityResponse(
            id=record.id,
            name=record.name,
            entity_type=record.entity_type,
            description=record.description,
            attributes=record.attributes if isinstance(record.attributes, dict) else {},
            aliases=record.aliases if isinstance(record.aliases, list) else [],
            workspace=record.workspace,
            project=record.project,
            created_at=record.created_at,
        )


class RelationshipService:
    """Business service handling relationship edge operations."""

    def __init__(self, repository: KnowledgeGraphRepository) -> None:
        self.repository = repository
        logger.info("relationship_service_initialized")

    async def create_relationship(self, request: RelationshipCreateRequest) -> RelationshipResponse:
        """Creates and persists a graph relationship edge."""
        record = await self.repository.save_relationship(
            source_id=request.source_id,
            target_id=request.target_id,
            relationship_type=request.relationship_type,
            weight=request.weight,
            attributes=request.attributes,
            workspace=request.workspace,
            project=request.project,
        )

        return RelationshipResponse(
            id=record.id,
            source_id=record.source_id,
            target_id=record.target_id,
            relationship_type=record.relationship_type,
            weight=record.weight,
            attributes=record.attributes if isinstance(record.attributes, dict) else {},
            workspace=record.workspace,
            project=record.project,
            created_at=record.created_at,
        )


class GraphQueryService:
    """Business service handling domain graph queries and traversals."""

    def __init__(self, repository: KnowledgeGraphRepository) -> None:
        self.repository = repository
        self.query_engine = GraphQueryEngine()
        self.traversal_engine = GraphTraversalEngine()
        logger.info("graph_query_service_initialized")

    async def query_graph(self, query: str, workspace: Optional[str] = None) -> List[Dict[str, Any]]:
        """Executes general graph query."""
        return await self.query_engine.search_engine.search_entities(query, limit=20)

    async def find_shortest_path(self, start_id: str, end_id: str) -> GraphPathResponse:
        """Calculates shortest path trace between nodes."""
        path_res = await self.traversal_engine.shortest_path(start_id, end_id)
        return GraphPathResponse(
            start_entity_id=path_res["start_entity_id"],
            end_entity_id=path_res["end_entity_id"],
            path_nodes=path_res["path_nodes"],
            path_edges=path_res["path_edges"],
            hop_count=path_res["hop_count"],
            total_weight=path_res["total_weight"],
        )


class ReasoningService:
    """Business service handling graph reasoning and impact analysis."""

    def __init__(self, repository: KnowledgeGraphRepository) -> None:
        self.repository = repository
        self.reasoner = GraphReasoner()
        logger.info("reasoning_service_initialized")

    async def analyze_impact(self, target_entity_id: str) -> Dict[str, Any]:
        """Performs impact analysis for target entity."""
        return await self.reasoner.analyze_impact(target_entity_id)


class KnowledgeGraphService:
    """Unified master business service."""

    def __init__(self, repository: KnowledgeGraphRepository) -> None:
        self.repository = repository
        self.builder = GraphBuilder()
        self.visualizer = GraphVisualizer()
        self.stats_tracker = GraphStatisticsTracker()
        self.health_checker = GraphHealthChecker()

        self.entity_service = EntityService(repository)
        self.relationship_service = RelationshipService(repository)
        self.query_service = GraphQueryService(repository)
        self.reasoning_service = ReasoningService(repository)

        logger.info("knowledge_graph_service_initialized")

    async def get_statistics(self) -> GraphStatisticsResponse:
        """Returns topological graph telemetry."""
        e_count = await self.repository.count_entities()
        r_count = await self.repository.count_relationships()
        self.stats_tracker.entity_count = e_count
        self.stats_tracker.relationship_count = r_count
        return self.stats_tracker.get_statistics()

    async def check_health(self) -> GraphHealthResponse:
        """Runs graph diagnostic health checks."""
        return self.health_checker.run_health_checks()
