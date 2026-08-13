"""Dependency Resolver detecting execution blockages and circular loops.
"""

from typing import Dict, Any, List, Set

class DependencyResolver:
    """Resolves scheduling blockages across planning DAG structures."""

    def find_blocking_tasks(self, nodes: Dict[str, Any]) -> List[str]:
        """Exposes unresolved parent tasks which block downstream assignees."""
        blockers = []
        for node_id, node in nodes.items():
            # Support both dictionary representation and objects
            dependencies = getattr(node, "dependencies", []) if not isinstance(node, dict) else node.get("dependencies", [])
            for dep in dependencies:
                dep_id = dep if isinstance(dep, str) else getattr(dep, "task_id", "")
                if dep_id and dep_id not in blockers:
                    blockers.append(dep_id)
        return blockers

    def detect_cycles(self, nodes: Dict[str, Any]) -> bool:
        """Returns boolean value checking if cycle dependencies exist."""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            node = nodes.get(node_id, {})
            dependencies = getattr(node, "dependencies", []) if not isinstance(node, dict) else node.get("dependencies", [])
            for dep in dependencies:
                dep_id = dep if isinstance(dep, str) else getattr(dep, "task_id", "")
                if dep_id not in visited:
                    if dfs(dep_id):
                        return True
                elif dep_id in rec_stack:
                    return True
            rec_stack.remove(node_id)
            return False

        for node_id in nodes:
            if node_id not in visited:
                if dfs(node_id):
                    return True
        return False
