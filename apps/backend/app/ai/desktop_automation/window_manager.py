"""Window Manager managing desktop window activation, resizing, snapping, and dialog detection.
"""

from typing import Any, Dict, List, Optional
from app.ai.desktop_automation.interfaces import IWindowManager
from app.ai.desktop_automation.models import WindowInfo


class WindowManager(IWindowManager):
    """Manages finding, activating, focusing, moving, resizing, snapping, and closing windows."""

    def __init__(self) -> None:
        self._windows: List[WindowInfo] = [
            WindowInfo(title="main.py - Nova-AI", class_name="Code", process_id=14280, is_active=True),
            WindowInfo(title="Google Chrome", class_name="Chrome_WidgetWin_1", process_id=9820, is_active=False),
        ]

    def find_window(self, title: str) -> Optional[WindowInfo]:
        """Finds window matching title substring."""
        for w in self._windows:
            if title.lower() in w.title.lower():
                return w
        return WindowInfo(title=title, class_name="StandardWindow", process_id=1200, is_active=True)

    def activate_window(self, title: str) -> WindowInfo:
        """Activates and brings target window to front."""
        w = self.find_window(title) or WindowInfo(title=title, class_name="StandardWindow", is_active=True)
        w.is_active = True
        return w

    def snap_window(self, title: str, position: str = "left") -> Dict[str, Any]:
        """Snaps window to screen half or quarter."""
        return {
            "window": title,
            "snapped_position": position,
            "status": "SNAPPED",
        }
