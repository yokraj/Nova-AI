"""Checkpoint Manager producing snapshots of workflows progress state history.
"""

import uuid
from datetime import datetime
from app.ai.workflow.models import Workflow, WorkflowCheckpoint
from app.ai.workflow.workflow_context import WorkflowContextContainer

class CheckpointManager:
    """Creates, serializes, and restores checkpoints."""

    def create_checkpoint(self, workflow: Workflow, context: WorkflowContextContainer) -> WorkflowCheckpoint:
        """Serializes snapshots of workflow and context parameters."""
        checkpoint_id = f"ckpt_{uuid.uuid4().hex[:8]}"
        return WorkflowCheckpoint(
            checkpoint_id=checkpoint_id,
            workflow_id=workflow.workflow_id,
            timestamp=datetime.utcnow(),
            workflow_snapshot=workflow.model_dump(),
            context_snapshot=context.dump()
        )

    def restore(self, checkpoint: WorkflowCheckpoint) -> tuple[Workflow, Dict[str, Any]]:
        """Reconstructs state instances from serialized snapshots."""
        workflow = Workflow.model_validate(checkpoint.workflow_snapshot)
        context_vars = dict(checkpoint.context_snapshot)
        return workflow, context_vars
