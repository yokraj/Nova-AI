"""Validation Engine verifying task DAG schemas integrity limits.
"""

from app.ai.planner.models import DependencyGraph
from app.ai.planner.exceptions import ValidationError
from app.ai.planner.dependency_graph import DependencyGraphManager

class ValidationEngine:
    """Checks circular paths, unreachable dependencies, and missing agent assignments."""

    def validate_graph(self, graph: DependencyGraph) -> None:
        """Runs validation checks on the dependency graph."""
        # Validate cycle constraints
        manager = DependencyGraphManager(graph)
        manager.detect_cycles()

        # Validate unreachable dependencies
        for node_id, task in graph.nodes.items():
            for prerequisite_id in task.dependencies:
                if prerequisite_id not in graph.nodes:
                    raise ValidationError(f"Integrity check failed: task '{node_id}' references missing dependency '{prerequisite_id}'")

        # Validate assignment presence
        for node_id, task in graph.nodes.items():
            if not task.assignment:
                raise ValidationError(f"Integrity check failed: task '{node_id}' has no active agent assignment")
