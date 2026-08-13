"""Mock provider simulating dynamic workflow missions offline.
"""

from typing import Dict, Any

class MockMissionProvider:
    """Mock offline mission simulation provider."""

    def simulate_mission_run(self) -> Dict[str, Any]:
        """Returns completed mock execution report."""
        return {
            "mission_id": "mock_mission_123",
            "state": "completed",
            "progress": 100.0,
            "outcome": "success"
        }

    def simulate_decision(self, failures: int) -> str:
        """Returns autonomous decision recommendation string."""
        if failures > 3:
            return "pause"
        return "continue"
