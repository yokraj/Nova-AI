"""Local Knowledge Graph storing entity nodes, relation edges, and graph traversal.
"""

from typing import Dict, List, Optional
from app.ai.research.interfaces import IKnowledgeGraph
from app.ai.research.models import KnowledgeGraphEdge, KnowledgeGraphNode, KnowledgeType


class KnowledgeGraph(IKnowledgeGraph):
    """Local Knowledge Graph storing concept nodes, relationships, and traversal logic."""

    def __init__(self) -> None:
        self._nodes: Dict[str, KnowledgeGraphNode] = {}
        self._edges: List[KnowledgeGraphEdge] = []
        self._seed_default_graph()

    def _seed_default_graph(self) -> None:
        n1 = KnowledgeGraphNode(node_id="concept_ai_agents", label="AI Agents", type=KnowledgeType.CONCEPT)
        n2 = KnowledgeGraphNode(node_id="tech_fastapi", label="FastAPI Framework", type=KnowledgeType.TECHNOLOGY)
        n3 = KnowledgeGraphNode(node_id="repo_nova_ai", label="Nova-AI Repository", type=KnowledgeType.REPOSITORY)

        self.add_node(n1)
        self.add_node(n2)
        self.add_node(n3)

        e1 = KnowledgeGraphEdge(source_id="repo_nova_ai", target_id="tech_fastapi", relation="uses_framework")
        e2 = KnowledgeGraphEdge(source_id="repo_nova_ai", target_id="concept_ai_agents", relation="implements_concept")

        self.add_edge(e1)
        self.add_edge(e2)

    def add_node(self, node: KnowledgeGraphNode) -> None:
        """Adds node to local graph dictionary."""
        self._nodes[node.node_id] = node

    def add_edge(self, edge: KnowledgeGraphEdge) -> None:
        """Adds relation edge to graph edges list."""
        self._edges.append(edge)

    def get_node(self, node_id: str) -> Optional[KnowledgeGraphNode]:
        """Retrieves node by ID."""
        return self._nodes.get(node_id)

    def get_related_nodes(self, node_id: str) -> List[KnowledgeGraphNode]:
        """Traverses graph for outgoing and incoming connected nodes.

        Args:
            node_id: Target node identifier.

        Returns:
            List of connected KnowledgeGraphNode items.
        """
        connected_ids: set[str] = set()
        for edge in self._edges:
            if edge.source_id == node_id:
                connected_ids.add(edge.target_id)
            elif edge.target_id == node_id:
                connected_ids.add(edge.source_id)

        return [self._nodes[nid] for nid in connected_ids if nid in self._nodes]

    def export_graph_summary(self) -> Dict[str, int]:
        """Returns node count and edge count summary."""
        return {"nodes_count": len(self._nodes), "edges_count": len(self._edges)}
