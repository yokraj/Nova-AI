"""Graph Reasoner Module.

Implements structural graph reasoning: Dependency reasoning, Impact analysis,
Relationship explanation, Missing dependency detection, and Architectural reasoning.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.knowledge_graph.graph_query import GraphQueryEngine
from app.knowledge_graph.graph_traversal import GraphTraversalEngine

logger = structlog.get_logger(__name__)


class GraphReasoner:
    """Enterprise Knowledge Graph Algorithmic Reasoner."""

    def __init__(
        self,
        query_engine: Optional[GraphQueryEngine] = None,
        traversal_engine: Optional[GraphTraversalEngine] = None,
    ) -> None:
        self.query_engine = query_engine or GraphQueryEngine()
        self.traversal_engine = traversal_engine or GraphTraversalEngine()
        logger.info("graph_reasoner_initialized")

    async def analyze_impact(self, target_entity_id: str) -> Dict[str, Any]:
        """Performs blast-radius impact analysis for modification of target entity."""
        affected_nodes = await self.traversal_engine.bfs_traversal(target_entity_id, max_depth=3)
        direct_deps = [n for n in affected_nodes if n.get("hop_depth") == 1]
        indirect_deps = [n for n in affected_nodes if n.get("hop_depth") > 1]

        logger.info("impact_analysis_completed", target_id=target_entity_id, total_affected=len(affected_nodes))
        return {
            "target_entity_id": target_entity_id,
            "total_affected_count": len(affected_nodes),
            "direct_impact_count": len(direct_deps),
            "indirect_impact_count": len(indirect_deps),
            "affected_entities": affected_nodes,
            "risk_assessment": "HIGH" if len(affected_nodes) > 5 else "LOW",
        }

    async def explain_relationship(self, source_id: str, target_id: str) -> Dict[str, Any]:
        """Provides structural path explanation between source and target entities."""
        path_res = await self.traversal_engine.shortest_path(source_id, target_id)
        nodes = path_res.get("path_nodes", [])

        explanation_steps = []
        for idx in range(len(nodes) - 1):
            n1 = nodes[idx]["name"]
            n2 = nodes[idx + 1]["name"]
            explanation_steps.append(f"Step {idx+1}: [{n1}] connects to [{n2}]")

        return {
            "source_id": source_id,
            "target_id": target_id,
            "path_length": path_res.get("hop_count", 0),
            "explanation_summary": " -> ".join([n["name"] for n in nodes]),
            "steps": explanation_steps,
        }

    async def detect_missing_dependencies(self, project_name: str) -> List[Dict[str, Any]]:
        """Detects unlinked or missing component dependencies in a project graph."""
        project_nodes = await self.query_engine.search_engine.search_project(project_name)
        missing = []
        for node in project_nodes:
            neighbors = await self.query_engine.search_engine.search_neighbors(node["id"])
            if not neighbors:
                missing.append({
                    "entity_id": node["id"],
                    "name": node["name"],
                    "entity_type": node.get("entity_type"),
                    "issue": "Isolated node with 0 degree connectivity.",
                })
        return missing
