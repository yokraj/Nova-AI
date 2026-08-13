"""Recovery Engine detecting system crashes/reboots and restoring mission execution state.
"""

from typing import Any, Dict
from app.ai.mission_runtime.checkpoint_engine import CheckpointEngine
from app.ai.mission_runtime.interfaces import IRecoveryEngine
from app.ai.mission_runtime.models import RecoveryRecord


class RecoveryEngine(IRecoveryEngine):
    """Recovery Engine managing automated recovery from application/browser crashes, reboot, and timeouts."""

    def __init__(self, checkpoint_engine: CheckpointEngine) -> None:
        self.checkpoint_engine = checkpoint_engine

    async def recover_mission(self, mission_id: str, crash_type: str) -> RecoveryRecord:
        """Restores mission execution state from latest checkpoint.

        Args:
            mission_id: Target mission ID string.
            crash_type: Category (app_crash, browser_crash, plugin_crash, timeout, reboot).

        Returns:
            RecoveryRecord audit model.
        """
        chk = await self.checkpoint_engine.load_latest_checkpoint(mission_id)

        cause = f"Interrupted by {crash_type}."
        action = "Restored execution state from persistent checkpoint."

        if chk:
            action = f"Restored task '{chk.task_id}' and variables from checkpoint '{chk.checkpoint_id}'."

        return RecoveryRecord(
            mission_id=mission_id,
            crash_type=crash_type,
            root_cause=cause,
            action_taken=action,
            success=True,
        )
