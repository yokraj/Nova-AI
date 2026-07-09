"""Workflow Services managing workflow lifecycles in Nova AI.

Handles creation, execution tasks mapping, cancellation tokens trigger,
and pause/resume transitions.
"""

import asyncio
from typing import Dict, Optional

from app.automation.engine import WorkflowExecutionEngine
from app.automation.models import (
    Workflow,
    WorkflowContext,
    WorkflowResult,
    WorkflowStatus,
)


class WorkflowService:
    """Orchestrates workflows lifecycle registry and execution tasks."""

    def __init__(self, execution_engine: WorkflowExecutionEngine) -> None:
        """Initializes the WorkflowService.

        Args:
            execution_engine: Target execution engine runner.
        """
        self.execution_engine = execution_engine
        self._workflows: Dict[str, Workflow] = {}
        self._contexts: Dict[str, WorkflowContext] = {}
        self._results: Dict[str, WorkflowResult] = {}
        self._active_tasks: Dict[str, asyncio.Task] = {}

    def create_workflow(self, workflow: Workflow) -> Workflow:
        """Saves a workflow definition inside cache registry.

        Args:
            workflow: The Workflow schema to register.

        Returns:
            The created Workflow object.
        """
        self._workflows[workflow.id] = workflow
        self._contexts[workflow.id] = WorkflowContext()
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Retrieves a registered workflow configuration.

        Args:
            workflow_id: Unique workflow identifier.

        Returns:
            The Workflow object, or None.
        """
        return self._workflows.get(workflow_id)

    def get_context(self, workflow_id: str) -> Optional[WorkflowContext]:
        """Gets execution state variables context.

        Args:
            workflow_id: Unique workflow identifier.

        Returns:
            The WorkflowContext object, or None.
        """
        return self._contexts.get(workflow_id)

    def get_result(self, workflow_id: str) -> Optional[WorkflowResult]:
        """Gets final execution stats result snapshot.

        Args:
            workflow_id: Unique workflow identifier.

        Returns:
            The WorkflowResult object, or None.
        """
        return self._results.get(workflow_id)

    async def execute_workflow(
        self, workflow_id: str, initial_variables: dict
    ) -> WorkflowResult:
        """Starts asynchronous workflow execution tracking task.

        Args:
            workflow_id: Target workflow identifier.
            initial_variables: Startup dictionary payload passed to context variables.

        Returns:
            The finalized WorkflowResult execution details.

        Raises:
            ValueError: If workflow is not registered.
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(
                f"Workflow with identifier '{workflow_id}' not found."
            )

        context = self.get_context(workflow_id) or WorkflowContext()
        context.variables.update(initial_variables)
        self._contexts[workflow_id] = context

        # Spawn task to allow cancel/pause control hooks
        task = asyncio.create_task(
            self.execution_engine.execute(workflow, context)
        )
        self._active_tasks[workflow_id] = task

        try:
            result = await task
            self._results[workflow_id] = result
            return result
        finally:
            self._active_tasks.pop(workflow_id, None)

    async def cancel_workflow(self, workflow_id: str) -> None:
        """Requests active execution cancellation.

        Args:
            workflow_id: Unique workflow identifier.
        """
        context = self.get_context(workflow_id)
        if context:
            context.is_cancelled = True
            context.log("cancellation_requested")

        task = self._active_tasks.get(workflow_id)
        if task:
            task.cancel()

    def pause_workflow(self, workflow_id: str) -> None:
        """Pauses a running workflow execution.

        Args:
            workflow_id: Unique workflow identifier.
        """
        workflow = self.get_workflow(workflow_id)
        if workflow and workflow.status == WorkflowStatus.RUNNING:
            workflow.status = WorkflowStatus.PAUSED
            context = self.get_context(workflow_id)
            if context:
                context.log("workflow_paused")

    def resume_workflow(self, workflow_id: str) -> None:
        """Resumes a paused workflow.

        Args:
            workflow_id: Unique workflow identifier.
        """
        workflow = self.get_workflow(workflow_id)
        if workflow and workflow.status == WorkflowStatus.PAUSED:
            workflow.status = WorkflowStatus.RUNNING
            context = self.get_context(workflow_id)
            if context:
                context.log("workflow_resumed")
