"""Priority Engine calculating critical path and updating tasks priority levels.
"""

from typing import Dict
from app.ai.planner.models import DependencyGraph

class PriorityEngine:
    """Updates task nodes priority levels ('Critical', 'High', 'Medium', 'Low') based on dependency depth."""

    def calculate_priorities(self, graph: DependencyGraph) -> None:
        """Updates graph critical_path lists and sets task priority fields."""
        depths: Dict[str, int] = {}
        for node_id in graph.nodes:
            depths[node_id] = self._get_depth(node_id, graph)

        max_depth = max(depths.values()) if depths else 0
        
        # Critical path nodes reside at top hierarchy depths
        critical_path = [node_id for node_id, depth in depths.items() if depth >= max_depth - 1]
        graph.critical_path = critical_path

        for node_id, task in graph.nodes.items():
            if node_id in critical_path:
                task.priority = "Critical"
            elif depths[node_id] >= 2:
                task.priority = "High"
            elif depths[node_id] == 1:
                task.priority = "Medium"
            else:
                task.priority = "Low"

    def _get_depth(self, node_id: str, graph: DependencyGraph) -> int:
        """Recursively checks max dependency depth of target node."""
        task = graph.nodes.get(node_id)
        if not task or not task.dependencies:
            return 0
        
        valid_deps = [dep for dep in task.dependencies if dep in graph.nodes]
        if not valid_deps:
            return 0
            
        return 1 + max(self._get_depth(dep, graph) for dep in valid_deps)
