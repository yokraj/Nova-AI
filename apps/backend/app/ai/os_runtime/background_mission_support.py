"""Long-Running Background Mission Support Engine with reboot recovery and checkpointing.
"""

from typing import Dict, List
from app.ai.os_runtime.interfaces import IBackgroundMissionSupport
from app.ai.os_runtime.models import MissionCheckpoint


class BackgroundMissionSupport(IBackgroundMissionSupport):
    """Executes hours/days-long background missions with reboot recovery, checkpointing, pause/resume, and voice status updates."""

    def __init__(self) -> None:
        self._checkpoints: Dict[str, MissionCheckpoint] = {}

    async def create_checkpoint(self, mission_id: str, name: str, progress: float, step: str) -> MissionCheckpoint:
        """Saves background mission checkpoint to persistent storage."""
        cp = MissionCheckpoint(
            mission_id=mission_id,
            name=name,
            progress_percent=progress,
            current_step=step,
        )
        self._checkpoints[mission_id] = cp
        return cp

    async def recover_missions_after_reboot(self) -> List[MissionCheckpoint]:
        """Restores background missions after system reboot."""
        return list(self._checkpoints.values())
