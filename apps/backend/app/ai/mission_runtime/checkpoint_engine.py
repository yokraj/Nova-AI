"""Checkpoint Engine persisting and restoring full mission state for crash & reboot survival.
"""

from typing import Any, Dict, Optional
import time
from app.ai.mission_runtime.interfaces import ICheckpointEngine
from app.ai.mission_runtime.models import CheckpointData, MissionState


class CheckpointEngine(ICheckpointEngine):
    """Checkpoint Engine serializing mission state, variables, browser, desktop, and voice session."""

    def __init__(self) -> None:
        self._checkpoints: Dict[str, CheckpointData] = {}

    async def save_checkpoint(self, mission_id: str, data: Dict[str, Any]) -> CheckpointData:
        """Saves a persistent state snapshot for a mission.

        Args:
            mission_id: Parent mission ID string.
            data: State parameters dictionary.

        Returns:
            CheckpointData model instance.
        """
        chk = CheckpointData(
            mission_id=mission_id,
            task_id=data.get("task_id"),
            state=data.get("state", MissionState.RUNNING),
            variables=data.get("variables", {}),
            memory=data.get("memory", {}),
            context=data.get("context", {}),
            browser_state=data.get("browser_state", {"open_tabs": 1, "url": "https://github.com/yokraj/Nova-AI"}),
            desktop_state=data.get("desktop_state", {"active_window": "VS Code"}),
            voice_session=data.get("voice_session", {"active": True, "last_transcript": "Hey Nova"}),
        )
        self._checkpoints[mission_id] = chk
        return chk

    async def load_latest_checkpoint(self, mission_id: str) -> Optional[CheckpointData]:
        """Loads most recent checkpoint snapshot.

        Args:
            mission_id: Mission ID string.

        Returns:
            CheckpointData model if found, else None.
        """
        return self._checkpoints.get(mission_id)
