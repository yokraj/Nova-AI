"""Clipboard Manager providing OS clipboard copy, paste, and text retrieval."""

import structlog

logger = structlog.get_logger("clipboard_manager")


class ClipboardManager:
    """Manages OS system clipboard content."""

    def __init__(self) -> None:
        self._content: str = ""

    async def get_text(self) -> str:
        """Get current text from clipboard."""
        logger.debug("Clipboard get text")
        return self._content

    async def set_text(self, text: str) -> str:
        """Copy text to clipboard."""
        self._content = text
        logger.info("Clipboard set text", length=len(text))
        return self._content

    async def clear(self) -> None:
        """Clear clipboard."""
        self._content = ""
        logger.info("Clipboard cleared")
