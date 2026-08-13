"""Event Bridge dispatching workflow lifecycle signals to system queues.
"""

import structlog
from typing import Any
from app.ai.workflow.models import Workflow, WorkflowStep

logger = structlog.get_logger("workflow_event_bridge")

class WorkflowEventBridge:
    """Listens to scheduler transitions and dispatches event trigger notifications."""

    def __init__(self, system_bus: Any = None) -> None:
        self.system_bus = system_bus

    async def publish_workflow_transition(self, workflow: Workflow) -> None:
        """Fires current workflow model snapshot on transitions."""
        if self.system_bus:
            try:
                await self.system_bus.publish("workflow_state_changed", {
                    "workflow_id": workflow.workflow_id,
                    "state": workflow.state.value,
                    "progress": workflow.progress
                })
            except Exception as err:
                logger.error("Failed to forward workflow signal via event bridge", error=str(err))

    async def publish_step_transition(self, step: WorkflowStep) -> None:
        """Fires current step model snapshot on transitions."""
        if self.system_bus:
            try:
                await self.system_bus.publish("workflow_step_changed", {
                    "step_id": step.step_id,
                    "state": step.state.value,
                    "retry_count": step.retry_count
                })
            except Exception as err:
                logger.error("Failed to forward step signal via event bridge", error=str(err))
