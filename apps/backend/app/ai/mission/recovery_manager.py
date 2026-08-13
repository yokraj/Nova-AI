"""Recovery Manager restoring crashed missions from checkpoints.
"""

import structlog
from typing import Optional, Tuple, Dict, Any
from app.ai.mission.models import Mission
from app.ai.mission.interfaces import IMissionPersistence
from app.ai.mission.checkpoint_manager import CheckpointManager

logger = structlog.get_logger("mission_recovery")

class RecoveryManager:
    """Restores executing contexts after restarts or crashes."""

    def __init__(self, persistence: IMissionPersistence, checkpoint_mgr: CheckpointManager) -> None:
        self.persistence = persistence
        self.checkpoint_mgr = checkpoint_mgr

    def recover_mission(self, mission_id: str) -> Optional[Tuple[Mission, Dict[str, Any]]]:
        """Loads and parses newest checkpoint snapshot."""
        logger.info("Triggered mission recovery coordinator", mission_id=mission_id)
        checkpoints = self.persistence.get_checkpoints(mission_id)
        if not checkpoints:
            logger.warn("No checkpoints registered for mission. Recovery aborted.", mission_id=mission_id)
            return None

        # Sort by timestamp (newest first)
        checkpoints.sort(key=lambda ck: ck.timestamp, reverse=True)
        latest_ckpt = checkpoints[0]

        mission, context_vars = self.checkpoint_mgr.restore(latest_ckpt)
        logger.info("Successfully recovered mission state from checkpoint snapshot", 
                    mission_id=mission_id, checkpoint_id=latest_ckpt.checkpoint_id)
        return mission, context_vars
