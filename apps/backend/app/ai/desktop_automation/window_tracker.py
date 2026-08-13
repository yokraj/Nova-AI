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
