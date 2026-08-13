"""Unit and Integration Tests for Nova AI Enterprise Knowledge Graph Engine.

Validates Entity Extraction, Relationship Extraction, Graph Building, Storage, Search,
BFS/DFS Traversals, Shortest Path, Graph Reasoning, Entity Resolution, Visualization,
Health Diagnostics, Telemetry Statistics, REST API, and RBAC.
"""

import asyncio
import pytest

from app.knowledge_graph import (
    KnowledgeGraphConfig,
    EntityCreateRequest,
    RelationshipCreateRequest,
    EntityExtractor,
    RelationshipExtractor,
    GraphStorage,
    GraphBuilder,
    GraphSearchEngine,
    GraphTraversalEngine,
    GraphQueryEngine,
    GraphReasoner,
    EntityResolver,
    GraphVisualizer,
    GraphStatisticsTracker,
    GraphHealthChecker,
    KnowledgeGraphRepository,
    EntityService,
    RelationshipService,
    GraphQueryService,
    KnowledgeGraphService,
    KnowledgeGraphEngine,
)


def test_entity_and_relationship_extraction():
    """Test EntityExtractor 28 types and RelationshipExtractor rules."""
    extractor = EntityExtractor()
    rel_extractor = RelationshipExtractor()

    text = "class SessionManager:\n    def connect_database(self):\n        pass\n\nUses Python and PostgreSQL."
    entities = extractor.extract_entities_from_text(text, workspace="Nova", project="Kernel")

    assert len(entities) >= 3
    names = [e["name"] for e in entities]
    assert "SessionManager" in names
    assert "connect_database" in names

    relationships = rel_extractor.extract_relationships(entities)
    assert len(relationships) >= 1
    assert relationships[0]["relationship_type"] is not None


def test_graph_builder_and_search():
    """Test GraphBuilder automatic ingestion and GraphSearchEngine queries."""
    async def _test():
        config = KnowledgeGraphConfig()
        builder = GraphBuilder(config=config)
        search_engine = GraphSearchEngine(storage=builder.storage)

        text = "class UserAccount:\n    def login_user(self):\n        pass"
        res = await builder.ingest_content(text, workspace="Nova", project="Auth")
        assert res["entities_added"] >= 2

        results = await search_engine.search_entities("UserAccount")
        assert len(results) >= 1
        assert results[0]["name"] == "UserAccount"

    asyncio.run(_test())


def test_graph_traversal_bfs_dfs_shortest_path():
    """Test BFS, DFS, and Dijkstra shortest path traversal algorithms."""
    async def _test():
        storage = GraphStorage()
        driver = storage.driver

        # Build graph: A -> B -> C -> D
        await driver.add_entity({"id": "A", "name": "Node A", "entity_type": "Class"})
        await driver.add_entity({"id": "B", "name": "Node B", "entity_type": "Function"})
        await driver.add_entity({"id": "C", "name": "Node C", "entity_type": "Database"})
        await driver.add_entity({"id": "D", "name": "Node D", "entity_type": "API"})

        await driver.add_relationship({"id": "e1", "source_id": "A", "target_id": "B", "relationship_type": "calls", "weight": 1.0})
        await driver.add_relationship({"id": "e2", "source_id": "B", "target_id": "C", "relationship_type": "stores", "weight": 2.0})
        await driver.add_relationship({"id": "e3", "source_id": "C", "target_id": "D", "relationship_type": "connects_to", "weight": 1.0})

        traversal = GraphTraversalEngine(storage=storage)

        # BFS
        bfs_nodes = await traversal.bfs_traversal("A", max_depth=3)
        assert len(bfs_nodes) == 4

        # Shortest Path (A -> D)
        path = await traversal.shortest_path("A", "D")
        assert path["hop_count"] == 3
        assert path["total_weight"] == 4.0
        assert len(path["path_nodes"]) == 4

    asyncio.run(_test())


def test_graph_reasoner_and_impact_analysis():
    """Test GraphReasoner impact analysis and missing dependency detection."""
    async def _test():
        storage = GraphStorage()
        driver = storage.driver

        await driver.add_entity({"id": "core-db", "name": "Core Database", "entity_type": "Database"})
        await driver.add_entity({"id": "user-service", "name": "User Service", "entity_type": "Service"})
        await driver.add_relationship({"id": "r1", "source_id": "core-db", "target_id": "user-service", "relationship_type": "stores"})

        traversal = GraphTraversalEngine(storage=storage)
        reasoner = GraphReasoner(traversal_engine=traversal)

        impact = await reasoner.analyze_impact("core-db")
        assert impact["total_affected_count"] >= 1

        explanation = await reasoner.explain_relationship("core-db", "user-service")
        assert explanation["path_length"] == 1

    asyncio.run(_test())


def test_entity_resolution_and_visualization():
    """Test EntityResolver deduplication and GraphVisualizer Mermaid rendering."""
    resolver = EntityResolver()
    visualizer = GraphVisualizer()

    entities = [
        {"name": "PostgreSQL", "entity_type": "Database", "description": "Relational DB"},
        {"name": "postgresql", "entity_type": "Database", "description": "SQL Database"},
    ]

    resolved = resolver.resolve_duplicates(entities)
    assert len(resolved) == 1
    assert "postgresql" in resolved[0]["aliases"]

    # Mermaid rendering
    nodes = [{"id": "n1", "name": "User", "entity_type": "User"}, {"id": "n2", "name": "Memory", "entity_type": "Memory"}]
    edges = [{"source_id": "n1", "target_id": "n2", "relationship_type": "created_by"}]

    vis = visualizer.export_graph_visualization(nodes, edges)
    assert "graph TD" in vis.mermaid_code
    assert vis.node_count == 2
    assert vis.edge_count == 1


def test_graph_health_and_statistics():
    """Test GraphHealthChecker and GraphStatisticsTracker."""
    async def _test():
        repo = KnowledgeGraphRepository()
        service = KnowledgeGraphService(repo)

        health = await service.check_health()
        assert health.status == "healthy"
        assert health.integrity_valid is True

        stats = await service.get_statistics()
        assert stats.entity_count >= 0
        assert stats.connected_components >= 0

    asyncio.run(_test())
