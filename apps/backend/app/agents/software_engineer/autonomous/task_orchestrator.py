"""Task Orchestrator structures topological task orders and maps step execution bounds.
"""

from typing import List
from app.agents.software_engineer.autonomous.interfaces import ITaskOrchestrator
from app.agents.software_engineer.autonomous.models import WorkflowStep

class LocalTaskOrchestrator(ITaskOrchestrator):
    """Orders execution plans to follow correct linear dependencies."""

    def order_tasks(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """Arranges list of tasks topologically based on pre-requisite dependencies."""
        # Simple topological sort: place steps without dependencies first, then respect dependencies
        ordered = []
        visited = set()
        step_dict = {s.id: s for s in steps}

        def visit(step_id: str):
            if step_id in visited:
                return
            step = step_dict.get(step_id)
            if not step:
                return
            for dep in step.dependencies:
                visit(dep)
            visited.add(step_id)
            ordered.append(step)

        for step in steps:
            visit(step.id)

        return ordered
