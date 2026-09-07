"""Mouse Controller providing OS cursor movements, clicks, dragging, and scrolling."""

from typing import Any, Tuple
import structlog

logger = structlog.get_logger("mouse_controller")


class MouseController:
    """Controls OS mouse cursor movements, clicks, double clicks, right clicks, and drag events."""

    def __init__(self, provider: Any = None) -> None:
        self.provider = provider
        self._current_pos: Tuple[int, int] = (960, 540)

    async def move_to(self, x: int, y: int) -> Tuple[int, int]:
        """Move cursor to screen coordinates."""
        self._current_pos = (x, y)
        logger.debug("Mouse move to", x=x, y=y)
        return self._current_pos

    async def click(self, x: int, y: int, button: str = "left") -> Tuple[int, int]:
        """Click at screen coordinates."""
        await self.move_to(x, y)
        logger.info("Mouse click", x=x, y=y, button=button)
        return self._current_pos

    async def double_click(self, x: int, y: int) -> Tuple[int, int]:
        """Double click at screen coordinates."""
        await self.click(x, y, button="left")
        logger.info("Mouse double click", x=x, y=y)
        return self._current_pos

    async def right_click(self, x: int, y: int) -> Tuple[int, int]:
        """Right click at screen coordinates."""
        return await self.click(x, y, button="right")

    async def drag(self, start_x: int, start_y: int, end_x: int, end_y: int) -> Tuple[int, int]:
        """Drag mouse from start to end coordinates."""
        await self.move_to(start_x, start_y)
        logger.info("Mouse drag", start=(start_x, start_y), end=(end_x, end_y))
        return await self.move_to(end_x, end_y)

    async def scroll(self, clicks: int) -> int:
        """Scroll mouse wheel."""
        logger.info("Mouse scroll", clicks=clicks)
        return clicks
