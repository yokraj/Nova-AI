"""History Manager tracking browser navigation history logs."""

from typing import List
import structlog

logger = structlog.get_logger("history_manager")


class HistoryManager:
    """Tracks browser navigation session history."""

    def __init__(self) -> None:
        self._history: List[str] = []

    async def add_history(self, url: str) -> None:
        """Record visited URL."""
        self._history.append(url)
        logger.debug("Recorded history URL", url=url)

    async def get_history(self) -> List[str]:
        """Get navigation history list."""
        return list(self._history)
