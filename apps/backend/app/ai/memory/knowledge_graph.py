"""Knowledge Graph models node relationships.
"""

from typing import Dict, Set, List, Tuple

class KnowledgeGraph:
    """Manages structural entity nodes and directional relationship edges (e.g. File imports Class, Class uses Function)."""

    def __init__(self) -> None:
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.adj: Dict[str, Set[str]] = {}
        self.edges_types: Dict[Tuple[str, str], str] = {}

    def add_node(self, node_id: str, label: str, properties: Dict[str, Any] = None) -> None:
        """Registers a node with properties."""
        self.nodes[node_id] = {
            "label": label,
            "properties": properties or {}
        }
        if node_id not in self.adj:
            self.adj[node_id] = set()

    def add_edge(self, source_id: str, target_id: str, relationship_type: str) -> None:
        """Registers a relationship edge between two nodes."""
        if source_id not in self.adj:
            self.add_node(source_id, "unknown")
        if target_id not in self.adj:
            self.add_node(target_id, "unknown")

        self.adj[source_id].add(target_id)
        self.edges_types[(source_id, target_id)] = relationship_type

    def get_neighbors(self, node_id: str) -> List[Tuple[str, str]]:
        """Returns direct neighbors and relationship type tags."""
        if node_id not in self.adj:
            return []
        return [
            (target, self.edges_types.get((node_id, target), "related"))
            for target in self.adj[node_id]
        ]

    def find_all_paths(self, start_id: str, depth: int = 2) -> List[str]:
        """Traverses the graph to build readable relationship descriptions."""
        if start_id not in self.nodes:
            return []

        results = []
        visited = set()

        def dfs(curr: str, current_depth: int, path: List[str]):
            if current_depth > depth:
                return
            
            node_lbl = self.nodes.get(curr, {}).get("label", "unknown")
            path.append(f"{curr} ({node_lbl})")
            results.append(" -> ".join(path))

            visited.add(curr)
            for neighbor in self.adj.get(curr, set()):
                if neighbor not in visited:
                    dfs(neighbor, current_depth + 1, list(path))
            visited.remove(curr)

        dfs(start_id, 1, [])
        return results
