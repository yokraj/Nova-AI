"""Checkpoint Manager serializing snapshots of active missions.
"""

import uuid
from datetime import datetime
from typing import Dict, Any
from app.ai.mission.models import Mission, MissionCheckpoint
from app.ai.mission.mission_context import MissionContextContainer

class CheckpointManager:
    """Produces and restores deep-copy snapshots of mission runs."""

    def create_checkpoint(self, mission: Mission, context: MissionContextContainer) -> MissionCheckpoint:
        """Serializes current states of target mission and variable context."""
        checkpoint_id = f"ckpt_{uuid.uuid4().hex[:8]}"
        return MissionCheckpoint(
            checkpoint_id=checkpoint_id,
            mission_id=mission.mission_id,
            timestamp=datetime.utcnow(),
            mission_snapshot=mission.model_dump(),
            context_snapshot=context.dump()
        )

    def restore(self, checkpoint: MissionCheckpoint) -> tuple[Mission, Dict[str, Any]]:
        """Reconstructs state instances from snapshot copies."""
        mission = Mission.model_validate(checkpoint.mission_snapshot)
        context_vars = dict(checkpoint.context_snapshot)
        return mission, context_vars
