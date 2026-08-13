"""Dependency Graph Manager implementing cycle checking and topological sorting.
"""

import structlog
from typing import Dict, List, Set
from app.ai.planner.models import DependencyGraph, Dependency
from app.ai.planner.exceptions import CycleError

logger = structlog.get_logger("dependency_graph")

class DependencyGraphManager:
    """Validates directional edges, preventing circular loops and resolving topological batches."""

    def __init__(self, graph: DependencyGraph) -> None:
        self.graph = graph

    def detect_cycles(self) -> None:
        """DFS cycle detection. Raises CycleError if back-edges are found."""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        adjacency = self._get_adjacency_list()

        def _dfs_has_cycle(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            for neighbor in adjacency.get(node_id, []):
                if neighbor not in visited:
                    if _dfs_has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.discard(node_id)
            return False

        for node_id in self.graph.nodes:
            if node_id not in visited:
                if _dfs_has_cycle(node_id):
                    raise CycleError(f"Circular dependency cycle detected, bottleneck node: '{node_id}'")

    def get_topological_sort(self) -> List[str]:
        """Resolves task dependency order topological sequence list."""
        self.detect_cycles()
        adjacency = self._get_adjacency_list()
        visited: Set[str] = set()
        stack: List[str] = []

        def _dfs_sort(node_id: str) -> None:
            visited.add(node_id)
            for neighbor in adjacency.get(node_id, []):
                if neighbor not in visited:
                    _dfs_sort(neighbor)
            stack.insert(0, node_id)

        for node_id in self.graph.nodes:
            if node_id not in visited:
                _dfs_sort(node_id)

        return stack

    def _get_adjacency_list(self) -> Dict[str, List[str]]:
        adj = {node_id: [] for node_id in self.graph.nodes}
        for edge in self.graph.edges:
            if edge.source_task_id in adj:
                adj[edge.source_task_id].append(edge.target_task_id)
        return adj
