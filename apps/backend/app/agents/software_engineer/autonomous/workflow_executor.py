"""Workflow Executor coordinates execution of steps in the active workflow.
"""

import time
from typing import Any, List, Optional
from app.agents.software_engineer.autonomous.interfaces import IWorkflowExecutor
from app.agents.software_engineer.autonomous.models import ExecutionContext, TaskExecution, Workflow, WorkflowStep
from app.runtime.events.event_bus import EventBus
from app.runtime.events.event import SystemEvent
from app.runtime.events.topics import Topic

class LocalWorkflowExecutor(IWorkflowExecutor):
    """Orchestrates step runs, health updates, and observability event notifications."""

    def __init__(self, agent: Optional[Any] = None, event_bus: Optional[EventBus] = None) -> None:
        self.agent = agent
        self.event_bus = event_bus or EventBus()

    async def execute_workflow(self, workflow: Workflow, context: ExecutionContext) -> List[TaskExecution]:
        """Runs workflow steps sequence, handling routing and emitting system events."""
        timeline = []
        
        # Publish WORKFLOW_STARTED event
        await self._publish_telemetry(Topic.WORKFLOW_STARTED, {
            "workflow_id": workflow.id,
            "project_name": context.project_name
        })

        for step in workflow.steps:
            step.status = "IN_PROGRESS"
            await self._publish_telemetry(Topic.TASK_STARTED, {
                "step_id": step.id,
                "step_name": step.name,
                "workflow_id": workflow.id
            })

            start_time = time.perf_counter()
            success = True
            error_message = None

            # Execute actual capability using routing if agent reference is active
            try:
                if self.agent:
                    await self._invoke_agent_capability(step.target_engine, context)
            except Exception as e:
                success = False
                error_message = str(e)

            duration = time.perf_counter() - start_time
            step.status = "COMPLETED" if success else "FAILED"

            exec_record = TaskExecution(
                step_id=step.id,
                success=success,
                duration_sec=duration,
                error_message=error_message
            )
            timeline.append(exec_record)

            topic = Topic.TASK_COMPLETED if success else Topic.TASK_FAILED
            await self._publish_telemetry(topic, {
                "step_id": step.id,
                "workflow_id": workflow.id,
                "duration_sec": duration,
                "error": error_message
            })

            if not success:
                # Break flow on failures for recovery/manual checks
                break

        # Publish WORKFLOW_COMPLETED event
        await self._publish_telemetry(Topic.WORKFLOW_COMPLETED, {
            "workflow_id": workflow.id,
            "success": all(t.success for t in timeline)
        })

        return timeline

    async def _invoke_agent_capability(self, engine_name: str, context: ExecutionContext) -> None:
        """Helper to invoke the correct software engineer agent capability."""
        # Clean naming matching agent properties
        if "Project Manager" in engine_name and hasattr(self.agent, "project_manager"):
            # Mock call since process_requirements is async
            await self.agent.project_manager.process_requirements("Simulated requirement processing")
        elif "Deployment" in engine_name and hasattr(self.agent, "deployment"):
            from app.agents.software_engineer.deployment.models import DeploymentRequest
            req = DeploymentRequest(project_path=context.workspace_root, environment="production")
            await self.agent.deployment.prepare_deployment(req)

    async def _publish_telemetry(self, topic: Topic, payload: dict) -> None:
        """Helper to broadcast telemetry event updates to system event bus."""
        event = SystemEvent(
            topic=topic,
            source="autonomous_integration_engine",
            payload=payload
        )
        try:
            await self.event_bus.publish(event)
        except Exception:
            # Prevent event bus failures from blocking main workflow execution
            pass
