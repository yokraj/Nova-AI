"""Mission Manager registering active missions and checkpoints.
"""

from typing import Dict, List, Optional
from app.ai.mission.models import Mission, MissionCheckpoint
from app.ai.mission.interfaces import IMissionPersistence

class MissionManager(IMissionPersistence):
    """Stores active missions and indexes checkpoints snapshots."""

    def __init__(self) -> None:
        self._missions: Dict[str, Mission] = {}
        self._checkpoints: Dict[str, List[MissionCheckpoint]] = {}

    def save_mission(self, mission: Mission) -> None:
        """Saves current mission state."""
        self._missions[mission.mission_id] = mission.model_copy()

    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """Retrieves active mission instance."""
        return self._missions.get(mission_id)

    def list_missions(self) -> List[Mission]:
        """Lists all registered missions."""
        return list(self._missions.values())

    def save_checkpoint(self, checkpoint: MissionCheckpoint) -> None:
        """Appends progress snapshot snapshot copy."""
        m_id = checkpoint.mission_id
        if m_id not in self._checkpoints:
            self._checkpoints[m_id] = []
        self._checkpoints[m_id].append(checkpoint)

    def get_checkpoints(self, mission_id: str) -> List[MissionCheckpoint]:
        """Retrieves checkpoints for target mission."""
        return self._checkpoints.get(mission_id, [])
