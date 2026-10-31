import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from app.ai.research.interfaces import IKnowledgeGraph
from app.ai.research.models import KnowledgeGraphEdge, KnowledgeGraphNode, KnowledgeType


class KnowledgeGraph(IKnowledgeGraph):
    """Local Knowledge Graph storing concept nodes, relationships, and traversal logic."""

    def __init__(self, seed: bool = True) -> None:
        self._nodes: Dict[str, KnowledgeGraphNode] = {}
        self._edges: List[KnowledgeGraphEdge] = []
        if seed:
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

    def get_nodes(self) -> Dict[str, KnowledgeGraphNode]:
        """Returns all nodes in graph."""
        return self._nodes

    def get_edges(self) -> List[KnowledgeGraphEdge]:
        """Returns all edges in graph."""
        return self._edges

    def get_edge(self, edge_id: str) -> Optional[KnowledgeGraphEdge]:
        """Retrieves edge by ID."""
        for e in self._edges:
            if e.edge_id == edge_id:
                return e
        return None

    def get_outgoing_edges(self, source_id: str) -> List[KnowledgeGraphEdge]:
        """Returns all outgoing edges originating from source_id."""
        return [e for e in self._edges if e.source_id == source_id]

    def get_incoming_edges(self, target_id: str) -> List[KnowledgeGraphEdge]:
        """Returns all incoming edges pointing to target_id."""
        return [e for e in self._edges if e.target_id == target_id]

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

    def clear(self) -> None:
        """Clears all nodes and edges from the graph."""
        self._nodes.clear()
        self._edges.clear()

    def export_graph_summary(self) -> Dict[str, int]:
        """Returns node count and edge count summary."""
        return {"nodes_count": len(self._nodes), "edges_count": len(self._edges)}

    def to_dict(self) -> Dict[str, Any]:
        """Serializes graph nodes and edges to dictionary."""
        return {
            "nodes": {nid: node.model_dump() for nid, node in self._nodes.items()},
            "edges": [edge.model_dump() for edge in self._edges],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeGraph":
        """Reconstructs KnowledgeGraph from serialized dictionary."""
        kg = cls(seed=False)
        nodes_data = data.get("nodes", {})
        for nid, nd in nodes_data.items():
            kg.add_node(KnowledgeGraphNode(**nd))
        edges_data = data.get("edges", [])
        for ed in edges_data:
            kg.add_edge(KnowledgeGraphEdge(**ed))
        return kg

    def save_to_json(self, file_path: Union[str, Path]) -> None:
        """Saves serialized graph state to a JSON file."""
        p = Path(file_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load_from_json(cls, file_path: Union[str, Path]) -> "KnowledgeGraph":
        """Loads serialized graph state from a JSON file."""
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"Knowledge graph file not found: {file_path}")
        data = json.loads(p.read_text(encoding="utf-8"))
        return cls.from_dict(data)

