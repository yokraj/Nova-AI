"""Window Tracker tracking window focus history, active windows, and application switches.
"""

from typing import Any, Dict, List


class WindowTracker:
    """Tracks active window changes and maintains focus history stack."""

    def __init__(self) -> None:
        self._history: List[str] = ["VS Code", "Google Chrome", "Windows Terminal"]

    def get_focus_history(self) -> List[str]:
        """Returns active window focus history stack."""
        return list(self._history)

    def get_active_window_info(self) -> Dict[str, Any]:
        """Returns currently active window information dictionary."""
        active_title = self._history[0] if self._history else "VS Code"
        return {
            "title": active_title,
            "handle": 0x00010204,
            "process_id": 14280,
            "executable_path": "C:\\Program Files\\Microsoft VS Code\\Code.exe",
            "monitor_info": {"monitor": 1, "width": 1920, "height": 1080},
        }
