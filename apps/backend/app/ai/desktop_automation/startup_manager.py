"""Startup Manager managing Windows startup applications and launch delay.
"""

from typing import Any, Dict, List


class StartupManager:
    """Manages Windows startup applications, enable/disable status, and startup impact."""

    def list_startup_apps(self) -> List[Dict[str, Any]]:
        """Returns startup applications list."""
        return [
            {"name": "Nova AI Agent OS Daemon", "status": "ENABLED", "impact": "LOW"},
            {"name": "OneDrive", "status": "DISABLED", "impact": "MEDIUM"},
        ]
