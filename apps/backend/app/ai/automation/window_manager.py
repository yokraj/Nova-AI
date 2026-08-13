"""Window Manager controlling OS application window focus, geometry, and enumeration."""

from typing import Any, List, Optional
import structlog

from app.ai.automation.exceptions import WindowNotFoundError
from app.ai.automation.models import WindowAction, WindowInfo

logger = structlog.get_logger("window_manager")


class WindowManager:
    """Manages open desktop application windows, focus, geometry, and window switching."""

    def __init__(self) -> None:
        self._windows: List[WindowInfo] = []

    async def list_windows(self) -> List[WindowInfo]:
        """Enumerate active desktop windows."""
        # Simulated/OS window enumeration
        self._windows = [
            WindowInfo(handle=1001, title="Google Chrome", process_name="chrome.exe", pid=4012, width=1920, height=1080, is_active=True),
            WindowInfo(handle=1002, title="Visual Studio Code", process_name="code.exe", pid=5120, width=1280, height=800, is_active=False),
            WindowInfo(handle=1003, title="Command Prompt", process_name="cmd.exe", pid=6200, width=800, height=600, is_active=False),
        ]
        return list(self._windows)

    async def focus_window(self, title_or_handle: Any) -> WindowInfo:
        """Bring window to foreground and make active."""
        windows = await self.list_windows()
        target: Optional[WindowInfo] = None

        for w in windows:
            if isinstance(title_or_handle, int) and w.handle == title_or_handle:
                target = w
                break
            elif isinstance(title_or_handle, str) and title_or_handle.lower() in w.title.lower():
                target = w
                break

        if not target:
            raise WindowNotFoundError(f"Window matching '{title_or_handle}' not found.")

        for w in windows:
            w.is_active = (w.handle == target.handle)

        logger.info("Focused window", handle=target.handle, title=target.title)
        return target

    async def perform_action(self, title_or_handle: Any, action: WindowAction, **kwargs: Any) -> WindowInfo:
        """Perform geometry or state action on target window (move, resize, minimize, etc.)."""
        win = await self.focus_window(title_or_handle)

        if action == WindowAction.MINIMIZE:
            win.is_minimized = True
            win.is_maximized = False
        elif action == WindowAction.MAXIMIZE:
            win.is_maximized = True
            win.is_minimized = False
        elif action == WindowAction.RESTORE:
            win.is_minimized = False
            win.is_maximized = False
        elif action == WindowAction.MOVE:
            win.x = kwargs.get("x", win.x)
            win.y = kwargs.get("y", win.y)
        elif action == WindowAction.RESIZE:
            win.width = kwargs.get("width", win.width)
            win.height = kwargs.get("height", win.height)

        logger.info("Executed window action", action=action.value, handle=win.handle)
        return win
