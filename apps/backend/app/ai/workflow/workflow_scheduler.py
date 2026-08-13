"""Workflow Scheduler managing scheduling queues and priorities.
"""

from typing import Dict, List, Set
from app.ai.workflow.models import Workflow, WorkflowStep, WorkflowState
from app.ai.workflow.interfaces import IWorkflowScheduler
from app.ai.workflow.dependency_manager import DependencyManager
from app.ai.workflow.execution_graph import ExecutionGraph

class WorkflowScheduler(IWorkflowScheduler):
    """Schedules step batches matching parent-child dependency trees."""

    def __init__(self) -> None:
        self.dependencies = DependencyManager()
        self.queue: Dict[str, Workflow] = {}

    def enqueue(self, workflow: Workflow) -> None:
        """Enqueues active workflow for scheduling checks."""
        self.queue[workflow.workflow_id] = workflow

    def get_next_steps(self, workflow_id: str) -> List[WorkflowStep]:
        """Resolves topological dependency blocks, yielding next eligible steps."""
        wf = self.queue.get(workflow_id)
        if not wf:
            return []

        # Find completed steps IDs
        completed = {
            step_id for step_id, step in wf.steps.items()
            if step.state == WorkflowState.COMPLETED
        }

        # Resolve unblocked steps
        unblocked = self.dependencies.get_unblocked_steps(wf.steps, completed)

        # Sort by topological order (dependencies first)
        graph = ExecutionGraph(wf.steps)
        topological_order = graph.get_topological_sort()
        
        # Sort unblocked steps matching topological sorting
        unblocked.sort(key=lambda s: topological_order.index(s.step_id))
        return unblocked
