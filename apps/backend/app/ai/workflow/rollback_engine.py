"""Rollback Engine restoring previous checkpoint contexts on failures.
"""

import structlog
from typing import Dict, Any
from app.ai.workflow.models import Workflow, WorkflowState
from app.ai.workflow.workflow_context import WorkflowContextContainer

logger = structlog.get_logger("rollback_engine")

class RollbackEngine:
    """Restores snapshots details on failure events."""

    def rollback(self, workflow: Workflow, context: WorkflowContextContainer, snapshot_data: Dict[str, Any]) -> None:
        """Restores workflow and context state fields to matching snapshot values."""
        logger.info("Triggered workflow section rollback", workflow_id=workflow.workflow_id)
        
        # Reset step states
        for step_id, step_snapshot in snapshot_data.get("steps", {}).items():
            if step_id in workflow.steps:
                workflow.steps[step_id].state = step_snapshot.get("state", WorkflowState.PENDING)
                workflow.steps[step_id].retry_count = step_snapshot.get("retry_count", 0)

        # Restore context variables
        context.load(snapshot_data.get("context", {}))
        workflow.state = WorkflowState.PENDING
        logger.info("Rollback completed successfully", workflow_id=workflow.workflow_id)
