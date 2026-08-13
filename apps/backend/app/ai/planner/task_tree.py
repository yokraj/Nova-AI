"""Task Tree helper providing traversals, search queries, and filtering.
"""

from typing import List, Optional
from app.ai.planner.models import TaskTree, TaskNode, Task

class TaskTreeHelper:
    """Traverses and queries TaskTree configurations flattened lists."""

    def __init__(self, tree: TaskTree) -> None:
        self.tree = tree

    def dfs(self) -> List[Task]:
        """Performs Depth-First Search traversal on tree nodes."""
        results: List[Task] = []
        def _visit(node: TaskNode) -> None:
            results.append(node.task)
            for child in node.children:
                _visit(child)
        _visit(self.tree.root_node)
        return results

    def bfs(self) -> List[Task]:
        """Performs Breadth-First Search traversal on tree nodes."""
        results: List[Task] = []
        queue: List[TaskNode] = [self.tree.root_node]
        while queue:
            current = queue.pop(0)
            results.append(current.task)
            queue.extend(current.children)
        return results

    def find_by_id(self, task_id: str) -> Optional[Task]:
        """Searches target task by identifier."""
        for task in self.dfs():
            if task.task_id == task_id:
                return task
        return None

    def filter_by_priority(self, priority: str) -> List[Task]:
        """Filters tree tasks list by priority levels."""
        return [
            task for task in self.dfs()
            if task.priority.lower() == priority.lower()
        ]
