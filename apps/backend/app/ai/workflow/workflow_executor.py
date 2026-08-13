"""Workflow Executor executing tasks via the Collaboration Engine.
"""

import structlog
from typing import Dict, Any
from app.ai.workflow.models import WorkflowStep, WorkflowState
from app.ai.workflow.exceptions import ExecutionError

logger = structlog.get_logger("workflow_executor")

class WorkflowExecutor:
    """Invokes specialist agents and maps step results context parameters."""

    def __init__(self, collab_engine: Any = None) -> None:
        self.collab_engine = collab_engine

    async def execute_step(self, step: WorkflowStep, context_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches step task details to specialist agents."""
        logger.info("Executing step task", step_id=step.step_id, agent=step.agent_id)
        step.state = WorkflowState.RUNNING

        if self.collab_engine:
            try:
                # Coordinate steps via collaboration engine routes
                collab_res = await self.collab_engine.collaborate(f"Execute {step.title}: {step.description}")
                step.state = WorkflowState.COMPLETED
                return collab_res
            except Exception as err:
                step.state = WorkflowState.FAILED
                step.error_message = str(err)
                raise ExecutionError(f"Workflow step execution failure: {str(err)}")
        else:
            # Fallback deterministic execution simulation
            step.state = WorkflowState.COMPLETED
            return {"outcome": "success", "agent_used": step.agent_id}
