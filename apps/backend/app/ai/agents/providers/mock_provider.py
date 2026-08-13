"""Mock Provider supplying mock environments values for offline agents testing.
"""

from typing import Dict, Any

class MockAgentProvider:
    """Mock environment configurations provider for test setups."""

    def get_mock_environment(self) -> Dict[str, Any]:
        """Returns offline system attributes."""
        return {
            "os": "windows",
            "offline_mode": True,
            "system_ram_gb": 16,
            "active_gpus_count": 0
        }
