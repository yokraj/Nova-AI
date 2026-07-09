"""Workflow planners and dependency DAG graph validators for Nova AI.

Coordinates step execution ordering and detects circular dependencies loops.
"""

from typing import Dict, List, Set

from app.automation.models import WorkflowStep


class DependencyGraph:
    """Represents a Directed Acyclic Graph (DAG) of execution steps."""

    def __init__(self, steps: List[WorkflowStep]) -> None:
        """Initializes the DependencyGraph.

        Args:
            steps: List of WorkflowStep objects configuration.
        """
        self.steps = steps
        self.adjacency: Dict[str, Set[str]] = {step.id: set() for step in steps}
        self.in_degree: Dict[str, int] = {step.id: 0 for step in steps}

        # Build graph: maps a dependency step -> list of steps depending on it
        for step in steps:
            for dep in step.dependencies:
                if dep in self.adjacency:
                    self.adjacency[dep].add(step.id)
                    self.in_degree[step.id] += 1

    def has_cycles(self) -> bool:
        """Determines if the graph contains any circular reference loops.

        Returns:
            True if a cycle is found; False otherwise.
        """
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in self.adjacency.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for step in self.steps:
            if step.id not in visited:
                if dfs(step.id):
                    return True
        return False


class ExecutionPlanner:
    """Calculates ordered, parallelizable execution steps layers."""

    @staticmethod
    def plan(steps: List[WorkflowStep]) -> List[List[WorkflowStep]]:
        """Groups workflow steps into sequential list of parallel execution levels.

        Args:
            steps: List of WorkflowStep configurations.

        Returns:
            A nested list of steps, where each sublist represents steps that
            can be processed concurrently.

        Raises:
            ValueError: If cycles are detected.
        """
        graph = DependencyGraph(steps)
        if graph.has_cycles():
            raise ValueError(
                "Workflow contains circular dependencies between execution steps."
            )

        steps_dict = {step.id: step for step in steps}
        in_degrees = dict(graph.in_degree)
        plan_levels: List[List[WorkflowStep]] = []

        while in_degrees:
            # Gather nodes whose dependencies are satisfied (in_degree is 0)
            level_nodes = [node for node, deg in in_degrees.items() if deg == 0]
            if not level_nodes:
                raise ValueError("Graph contains circular dependency loops.")

            level_steps = [steps_dict[node] for node in level_nodes]
            plan_levels.append(level_steps)

            # Prune resolved nodes from tracking lists and update remaining nodes
            for node in level_nodes:
                del in_degrees[node]
                for neighbor in graph.adjacency.get(node, []):
                    if neighbor in in_degrees:
                        in_degrees[neighbor] -= 1

        return plan_levels
