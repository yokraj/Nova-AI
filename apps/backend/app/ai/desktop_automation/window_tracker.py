"""Window Tracker tracking real window focus history, active windows, and application switches.

Uses real Win32 API calls via Win32ApiWrapper. Zero synthetic/hardcoded active window titles or handles.
"""

from typing import Any, Dict, List, Optional
from app.ai.desktop_automation.win32_api_wrapper import Win32ApiWrapper


class WindowTracker:
    """Tracks active window changes and maintains real focus history stack."""

    def __init__(self, win32_api: Optional[Win32ApiWrapper] = None, history_size: int = 25) -> None:
        self._history: List[str] = []
        self._history_objs: List[Any] = []
        self._history_size = history_size
        self._win32_api = win32_api or Win32ApiWrapper()

    def get_focus_history(self) -> List[Any]:
        """Returns active window focus history stack."""
        self.get_active_window_info()  # Refresh active window state
        return list(self._history_objs) if self._history_objs else list(self._history)

    def get_active_window(self) -> Any:
        """Returns WindowInfo-like object for active foreground window."""
        info = self.get_active_window_info()
        from app.ai.desktop_automation.models import WindowInfo
        return WindowInfo(
            title=info.get("title", ""),
            handle=str(info.get("handle", "0x0")),
            process_id=info.get("process_id", 0),
            process_name=info.get("executable_name", ""),
        )

    def get_active_window_info(self) -> Dict[str, Any]:
        """Returns currently active foreground window information dictionary from OS APIs."""
        info = self._win32_api.get_foreground_window_info()
        if info and info.get("title"):
            title = info["title"]
            if not self._history or self._history[0] != title:
                # Insert at top of focus history stack
                from app.ai.desktop_automation.models import WindowInfo
                win_obj = WindowInfo(
                    title=title,
                    handle=str(info.get("handle", "0x0")),
                    process_id=info.get("process_id", 0),
                    process_name=info.get("executable_name", ""),
                )
                if title in self._history:
                    self._history.remove(title)
                self._history.insert(0, title)
                self._history_objs.insert(0, win_obj)
                if len(self._history) > self._history_size:
                    self._history.pop()
                if len(self._history_objs) > self._history_size:
                    self._history_objs.pop()

            return {
                "title": title,
                "handle": info.get("handle", "0x0"),
                "process_id": info.get("process_id", 0),
                "executable_path": info.get("executable_path", ""),
                "executable_name": info.get("executable_name", ""),
                "monitor_info": info.get("bounds", {"width": 0, "height": 0}),
            }

        # If no active window handle or not on Windows
        return {
            "title": "",
            "handle": "0x0",
            "process_id": 0,
            "executable_path": "",
            "executable_name": "",
            "monitor_info": {"width": 0, "height": 0},
        }
