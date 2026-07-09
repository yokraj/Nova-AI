"""Workflow execution engine for running DAG tasks in Nova AI.

Orchestrates sequential and concurrent steps, applying retry limits, timeouts,
cancellation checks, variable mappings, and event dispatches.
"""

import asyncio
from datetime import datetime
from typing import Any, Callable, Dict, Optional
import structlog

from app.automation.event_bus import EventBus
from app.automation.models import (
    Workflow,
    WorkflowContext,
    WorkflowResult,
    WorkflowStatus,
    WorkflowStep,
)
from app.automation.planner import ExecutionPlanner

logger = structlog.get_logger(__name__)


class WorkflowExecutionEngine:
    """Core engine executing planned workflow tasks graphs."""

    def __init__(
        self, event_bus: EventBus, step_runner: Optional[Callable] = None
    ) -> None:
        """Initializes the WorkflowExecutionEngine.

        Args:
            event_bus: The application EventBus broker instance.
            step_runner: Optional step execution callback function.
        """
        self.event_bus = event_bus
        self.step_runner = step_runner or self._default_step_runner

    async def _default_step_runner(
        self, step: WorkflowStep, context: WorkflowContext
    ) -> Dict[str, Any]:
        """Default fallback mock executor mapping step variables inputs to outputs."""
        await asyncio.sleep(0.01)  # Simulate fast asynchronous execution delay
        inputs = {}
        for input_key, context_key in step.input_mapping.items():
            inputs[input_key] = context.variables.get(context_key)

        # Generate a standard mock output string incorporating inputs mapping
        return {"output": f"Result of {step.id} processed inputs {inputs}"}

    async def execute(
        self, workflow: Workflow, context: WorkflowContext
    ) -> WorkflowResult:
        """Runs the scheduled steps of a workflow to completion.

        Args:
            workflow: The target Workflow schema definition.
            context: Active transaction execution context.

        Returns:
            The completed WorkflowResult statistics output.
        """
        workflow.status = WorkflowStatus.RUNNING
        context.log("workflow_started")
        await self.event_bus.publish(
            "workflow_started", {"workflow_id": workflow.id}
        )

        try:
            # Order steps topologically into parallelizable tiers
            levels = ExecutionPlanner.plan(workflow.steps)
        except Exception as error:
            workflow.status = WorkflowStatus.FAILED
            context.log("workflow_failed", details={"error": str(error)})
            return WorkflowResult(
                workflow_id=workflow.id,
                status=workflow.status,
                variables=context.variables,
                history=context.history,
                error_message=str(error),
            )

        for level_steps in levels:
            if context.is_cancelled:
                workflow.status = WorkflowStatus.CANCELLED
                context.log("workflow_cancelled")
                await self.event_bus.publish(
                    "workflow_cancelled", {"workflow_id": workflow.id}
                )
                break

            if workflow.status in (
                WorkflowStatus.PAUSED,
                WorkflowStatus.FAILED,
            ):
                break

            # Execute all steps in the current execution layer concurrently (parallel execution)
            tasks = [
                self._run_step_with_retry(step, context)
                for step in level_steps
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Analyze level execution results
            for idx, result in enumerate(results):
                step = level_steps[idx]
                if isinstance(result, Exception):
                    workflow.status = WorkflowStatus.FAILED
                    context.log(
                        "workflow_failed",
                        step_id=step.id,
                        details={"error": str(result)},
                    )
                    await self.event_bus.publish(
                        "workflow_failed",
                        {
                            "workflow_id": workflow.id,
                            "error_message": str(result),
                        },
                    )
                    break
                elif step.status == WorkflowStatus.FAILED:
                    workflow.status = WorkflowStatus.FAILED
                    context.log(
                        "workflow_failed",
                        step_id=step.id,
                        details={"error": step.error},
                    )
                    await self.event_bus.publish(
                        "workflow_failed",
                        {
                            "workflow_id": workflow.id,
                            "error_message": step.error,
                        },
                    )
                    break

            if workflow.status == WorkflowStatus.FAILED:
                break

        if workflow.status == WorkflowStatus.RUNNING:
            workflow.status = WorkflowStatus.COMPLETED
            context.log("workflow_completed")
            await self.event_bus.publish(
                "workflow_completed", {"workflow_id": workflow.id}
            )

        # Extract last error message if execution failed
        last_error = None
        if workflow.status == WorkflowStatus.FAILED:
            failed_steps = [
                s for s in workflow.steps if s.status == WorkflowStatus.FAILED
            ]
            if failed_steps:
                last_error = failed_steps[0].error

        return WorkflowResult(
            workflow_id=workflow.id,
            status=workflow.status,
            variables=context.variables,
            history=context.history,
            error_message=last_error,
        )

    async def _run_step_with_retry(
        self, step: WorkflowStep, context: WorkflowContext
    ) -> None:
        """Executes a single step configuration with timeout constraints and retries.

        Args:
            step: The target WorkflowStep to process.
            context: Active variables execution context.
        """
        step.status = WorkflowStatus.RUNNING
        step.started_at = datetime.utcnow()
        context.log("step_started", step_id=step.id)
        await self.event_bus.publish("step_started", {"step_id": step.id})

        attempts = 0
        max_attempts = step.retry_limit + 1

        while attempts < max_attempts:
            if context.is_cancelled:
                step.status = WorkflowStatus.CANCELLED
                context.log("step_cancelled", step_id=step.id)
                await self.event_bus.publish(
                    "step_cancelled", {"step_id": step.id}
                )
                return

            attempts += 1
            try:
                timeout = step.timeout_seconds or 30.0
                # Await runner within timeout block
                outputs = await asyncio.wait_for(
                    self.step_runner(step, context), timeout=timeout
                )

                # Set outputs mapping values back to context variables dictionary
                for output_key, context_key in step.output_mapping.items():
                    context.variables[context_key] = outputs.get(output_key)

                step.status = WorkflowStatus.COMPLETED
                step.completed_at = datetime.utcnow()
                context.log("step_completed", step_id=step.id)
                await self.event_bus.publish(
                    "step_completed", {"step_id": step.id}
                )
                return

            except Exception as error:
                error_msg = str(error) or error.__class__.__name__
                step.error = error_msg
                context.log(
                    "step_attempt_failed",
                    step_id=step.id,
                    details={"attempt": attempts, "error": error_msg},
                )
                if attempts >= max_attempts:
                    step.status = WorkflowStatus.FAILED
                    step.completed_at = datetime.utcnow()
                    context.log(
                        "step_failed", step_id=step.id, details={"error": error_msg}
                    )
                    await self.event_bus.publish(
                        "step_failed", {"step_id": step.id, "error": error_msg}
                    )
                    raise error
                else:
                    # Exponential backoff delay retry loops
                    await asyncio.sleep(2**attempts * 0.05)
