"""Keyboard Controller providing OS keyboard typing, key combinations, and hotkeys."""

from typing import List
import structlog

logger = structlog.get_logger("keyboard_controller")


class KeyboardController:
    """Controls OS keyboard input, text typing, key presses, and hotkey combinations."""

    async def type_text(self, text: str) -> str:
        """Simulate typing text characters."""
        logger.info("Keyboard type text", text_length=len(text))
        return text

    async def press_key(self, key_name: str) -> str:
        """Simulate single key press (e.g. Enter, Escape, Tab)."""
        logger.info("Keyboard press key", key=key_name)
        return key_name

    async def hotkey(self, keys: List[str]) -> List[str]:
        """Simulate hotkey combination (e.g. ['ctrl', 'c'], ['alt', 'tab'])."""
        combo = "+".join(keys)
        logger.info("Keyboard hotkey combination", combo=combo)
        return keys
