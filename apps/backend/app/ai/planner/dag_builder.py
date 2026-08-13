"""DAG Builder translating task tree branches into sequential dependency flows.
"""

from app.ai.planner.models import TaskTree, DependencyGraph, Dependency, TaskNode
from app.ai.planner.task_tree import TaskTreeHelper
from app.ai.planner.utils import generate_uuid

class DAGBuilder:
    """Flattens trees, auto-assigning directional dependency edges between siblings."""

    def build_dag(self, task_tree: TaskTree) -> DependencyGraph:
        """Converts TaskTree to a populated DependencyGraph DAG."""
        nodes = {}
        edges = []

        # Flatten tree
        helper = TaskTreeHelper(task_tree)
        for task in helper.dfs():
            nodes[task.task_id] = task

        # Auto-link sibling nodes to establish execution phases sequences
        def _link_siblings(node: TaskNode) -> None:
            for i in range(1, len(node.children)):
                prev_task = node.children[i - 1].task
                curr_task = node.children[i].task

                # Current task depends on previous task completing
                curr_task.dependencies.append(prev_task.task_id)
                edges.append(Dependency(
                    dependency_id=generate_uuid(),
                    source_task_id=prev_task.task_id,
                    target_task_id=curr_task.task_id
                ))

            for child in node.children:
                _link_siblings(child)

        _link_siblings(task_tree.root_node)

        return DependencyGraph(nodes=nodes, edges=edges)
