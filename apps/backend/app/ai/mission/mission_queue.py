"""Mission Queue supporting FIFO and priority missions.
"""

from typing import Dict, List, Optional
from app.ai.mission.models import Mission, MissionState
from app.ai.mission.exceptions import QueueError

class MissionQueue:
    """Manages active, priority, and queued mission objects list."""

    def __init__(self) -> None:
        self._queue: List[Mission] = []

    def push(self, mission: Mission) -> None:
        """Appends mission to queue and tags its state as queued."""
        mission.state = MissionState.QUEUED
        self._queue.append(mission)

    def pop(self) -> Optional[Mission]:
        """Pops FIFO queue item."""
        if not self._queue:
            return None
        return self._queue.pop(0)

    def cancel(self, mission_id: str) -> bool:
        """Removes target mission ID from scheduling list."""
        for idx, mission in enumerate(self._queue):
            if mission.mission_id == mission_id:
                self._queue.pop(idx)
                return True
        return False

    def list_queued(self) -> List[Mission]:
        """Returns copy of active queued missions list."""
        return list(self._queue)
