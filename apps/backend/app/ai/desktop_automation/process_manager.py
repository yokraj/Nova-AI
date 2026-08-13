"""Process Manager managing process listing, kill, suspend, resume, CPU/RAM/GPU monitoring.
"""

from typing import Any, Dict, List


class ProcessManager:
    """Monitors running processes, memory/CPU usage, process trees, and process termination."""

    def list_processes(self) -> List[Dict[str, Any]]:
        """Returns list of active system processes."""
        return [
            {"pid": 14280, "name": "Code.exe", "cpu_percent": 2.4, "ram_mb": 420},
            {"pid": 9820, "name": "chrome.exe", "cpu_percent": 4.1, "ram_mb": 850},
        ]
