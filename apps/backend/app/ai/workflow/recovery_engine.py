"""Recovery Engine recovering workflows from target checkpoints after crash events.
"""

import structlog
from typing import Optional, Tuple, Dict, Any
from app.ai.workflow.models import Workflow
from app.ai.workflow.interfaces import IWorkflowPersistence
from app.ai.workflow.checkpoint_manager import CheckpointManager

logger = structlog.get_logger("recovery_engine")

class RecoveryEngine:
    """Restores crashed workflow states using serialized snapshot histories."""

    def __init__(self, persistence: IWorkflowPersistence, checkpoint_mgr: CheckpointManager) -> None:
        self.persistence = persistence
        self.checkpoint_mgr = checkpoint_mgr

    def recover_workflow(self, workflow_id: str) -> Optional[Tuple[Workflow, Dict[str, Any]]]:
        """Restores workflow and context snapshot from last saved checkpoint."""
        logger.info("Triggered workflow recovery process", workflow_id=workflow_id)
        checkpoints = self.persistence.get_checkpoints(workflow_id)
        if not checkpoints:
            logger.warn("No checkpoints registered for workflow. Recovery aborted.", workflow_id=workflow_id)
            return None

        # Sort by timestamp (newest first)
        checkpoints.sort(key=lambda ck: ck.timestamp, reverse=True)
        latest_ckpt = checkpoints[0]

        workflow, context_vars = self.checkpoint_mgr.restore(latest_ckpt)
        logger.info("Successfully recovered workflow from checkpoint snapshot", 
                    workflow_id=workflow_id, checkpoint_id=latest_ckpt.checkpoint_id)
        return workflow, context_vars
