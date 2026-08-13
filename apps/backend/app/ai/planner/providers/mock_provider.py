"""Mock Provider supplying deterministic offline configurations templates.
"""

from typing import Dict, Any

class MockPlannerProvider:
    """Mock planning provider returning mock environment stats."""

    def generate_mock_plan(self) -> Dict[str, Any]:
        """Returns standard offline mock settings."""
        return {
            "mode": "offline_mock",
            "provider_type": "deterministic",
            "offline_ready": True
        }
