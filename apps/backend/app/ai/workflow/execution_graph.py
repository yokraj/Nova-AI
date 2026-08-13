"""Execution Graph modeling workflow step nodes and topological routing routes.
"""

from typing import Dict, List, Set
from app.ai.workflow.models import WorkflowStep
from app.ai.workflow.exceptions import ExecutionError

class ExecutionGraph:
    """DAG compiler resolving step dependency execution paths."""

    def __init__(self, steps: Dict[str, WorkflowStep]) -> None:
        self.steps = steps

    def get_topological_sort(self) -> List[str]:
        """Runs topological sorting on steps and returns lists of step IDs."""
        visited: Set[str] = set()
        stack: List[str] = []
        rec_stack: Set[str] = set()

        def dfs(node_id: str):
            visited.add(node_id)
            rec_stack.add(node_id)
            step = self.steps.get(node_id)
            if step:
                for dep in step.dependencies:
                    if dep not in visited:
                        dfs(dep)
                    elif dep in rec_stack:
                        raise ExecutionError("Cyclic step dependency path detected in execution graph")
            rec_stack.remove(node_id)
            stack.append(node_id)

        for step_id in self.steps:
            if step_id not in visited:
                dfs(step_id)

        return stack
