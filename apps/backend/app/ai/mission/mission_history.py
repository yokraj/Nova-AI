"""Mission History tracking state change transitions log files.
"""

from datetime import datetime
from typing import List, Dict, Any

class MissionHistory:
    """Logs lifecycle state change logs for auditing."""

    def __init__(self, mission_id: str) -> None:
        self.mission_id = mission_id
        self.logs: List[Dict[str, Any]] = []

    def record_transition(self, from_state: str, to_state: str, details: str = "") -> None:
        """Appends transition event log."""
        self.logs.append({
            "timestamp": datetime.utcnow().isoformat(),
            "from_state": from_state,
            "to_state": to_state,
            "details": details
        })
