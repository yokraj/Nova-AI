"""Workflow Recorder observing user actions and generating reusable workflow macros.
"""

from typing import Any, Dict, List
from app.ai.mission_runtime.interfaces import IWorkflowRecorder
from app.ai.mission_runtime.models import TaskItem, WorkflowDefinition, WorkflowType


class WorkflowRecorder(IWorkflowRecorder):
    """Workflow Recorder compiling recorded user actions into reusable workflow definitions."""

    async def record_workflow(self, actions: List[Dict[str, Any]], name: str) -> WorkflowDefinition:
        """Converts raw recorded actions into structured WorkflowDefinition.

        Args:
            actions: List of user action dicts (e.g. click, type, navigate).
            name: Title for recorded macro.

        Returns:
            WorkflowDefinition instance.
        """
        tasks: List[TaskItem] = []

        for idx, act in enumerate(actions):
            task_title = act.get("description", f"Recorded Action {idx+1}: {act.get('type', 'step')}")
            task = TaskItem(
                title=task_title,
                action_type=act.get("type", "browser_action"),
                subsystem="automation_runtime",
                parameters=act,
            )
            tasks.append(task)

        if not tasks:
            tasks.append(TaskItem(title=f"Macro Step 1 for {name}", action_type="macro"))

        return WorkflowDefinition(
            name=name,
            type=WorkflowType.SEQUENTIAL,
            tasks=tasks,
        )
