"""Abstract interfaces for components of the Mission Control Engine.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.ai.mission.models import Mission, MissionCheckpoint

class IMissionPersistence(ABC):
    """Abstract store for registering and archiving missions."""

    @abstractmethod
    def save_mission(self, mission: Mission) -> None:
        """Saves current mission state."""
        pass

    @abstractmethod
    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """Retrieves active mission instance."""
        pass

    @abstractmethod
    def list_missions(self) -> List[Mission]:
        """Lists all registered missions."""
        pass

    @abstractmethod
    def save_checkpoint(self, checkpoint: MissionCheckpoint) -> None:
        """Stores checkpoint snapshot log."""
        pass

    @abstractmethod
    def get_checkpoints(self, mission_id: str) -> List[MissionCheckpoint]:
        """Retrieves checkpoints for target mission."""
        pass
