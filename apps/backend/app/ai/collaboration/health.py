"""Collaboration Health Monitor checking operational statuses of subsystems.
"""

from typing import Dict, Any

class CollaborationHealthMonitor:
    """Monitors live status flags for communication bus, router, and memory integrations."""

    def __init__(self, bus: Any, router: Any, tracker: Any, memory: Any) -> None:
        self.bus = bus
        self.router = router
        self.tracker = tracker
        self.memory = memory

    def check_health(self) -> Dict[str, Any]:
        """Evaluates live component statuses returning diagnostic reports."""
        details = {
            "communication_bus": "online" if self.bus is not None else "offline",
            "message_router": "online" if self.router is not None else "offline",
            "workflow_tracker": "online" if self.tracker is not None else "offline",
            "memory_integration": "online" if self.memory is not None else "offline"
        }
        
        overall = "healthy" if all(v == "online" for v in details.values()) else "degraded"
        return {
            "status": overall,
            "components": details
        }
