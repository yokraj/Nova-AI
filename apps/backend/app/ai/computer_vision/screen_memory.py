"""Screen Memory store keeping historical screen captures, navigation paths, and visual state changes.
"""

from typing import Any, Dict, List, Optional
from app.ai.computer_vision.interfaces import IScreenMemory
from app.ai.computer_vision.models import DesktopScene, ScreenHistoryItem


class ScreenMemory(IScreenMemory):
    """In-memory visual history store for navigation and visual change detection."""

    def __init__(self, limit: int = 50) -> None:
        self._limit = limit
        self._history: List[ScreenHistoryItem] = []

    async def record_screen(self, scene: DesktopScene, action: Optional[str] = None) -> None:
        """Records a screen capture event into visual memory.

        Args:
            scene: DesktopScene model instance.
            action: Optional action executed on screen.
        """
        item = ScreenHistoryItem(
            window_title=scene.active_window_title,
            process_name=scene.process_name,
            screenshot_hash=f"hash_{scene.scene_id}",
            action_taken=action or "capture_snapshot",
        )
        self._history.append(item)
        if len(self._history) > self._limit:
            self._history.pop(0)

    async def get_history(self, limit: int = 10) -> List[ScreenHistoryItem]:
        """Returns recent screen memory records."""
        return self._history[-limit:]
