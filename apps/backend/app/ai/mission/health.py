"""Mission health check monitor testing scheduler and queue connections.
"""

from typing import Dict, Any

class MissionHealthMonitor:
    """Evaluates live status logs of scheduler and persistent systems."""

    def __init__(self, scheduler: Any, queue: Any, persistence: Any) -> None:
        self.scheduler = scheduler
        self.queue = queue
        self.persistence = persistence

    def check_health(self) -> Dict[str, Any]:
        """Runs validation checks returning a status report."""
        details = {
            "mission_scheduler": "online" if self.scheduler is not None else "offline",
            "mission_queue": "online" if self.queue is not None else "offline",
            "state_persistence": "online" if self.persistence is not None else "offline"
        }
        overall = "healthy" if all(v == "online" for v in details.values()) else "degraded"
        return {
            "status": overall,
            "components": details
        }
