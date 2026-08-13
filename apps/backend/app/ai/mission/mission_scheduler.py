"""Mission Scheduler selecting execution order and resources allocation bounds.
"""

from typing import List, Optional
from app.ai.mission.models import Mission, MissionState
from app.ai.mission.mission_queue import MissionQueue

class MissionScheduler:
    """Manages active concurrent schedules."""

    def __init__(self, queue: MissionQueue, max_concurrency: int = 3) -> None:
        self.queue = queue
        self.max_concurrency = max_concurrency
        self.active_missions: List[Mission] = []

    def schedule_next(self) -> Optional[Mission]:
        """Resolves concurrency limits and schedules next eligible queued mission."""
        if len(self.active_missions) >= self.max_concurrency:
            return None

        mission = self.queue.pop()
        if mission:
            mission.state = MissionState.PLANNING
            self.active_missions.append(mission)
        return mission

    def complete_mission(self, mission_id: str) -> None:
        """Removes mission from active execution bounds."""
        self.active_missions = [
            m for m in self.active_missions 
            if m.mission_id != mission_id
        ]
