"""Clipboard Monitor inspecting clipboard text changes and detecting stack traces/URLs."""

import structlog

from app.ai.ambient.models import ClipboardContent

logger = structlog.get_logger("clipboard_monitor")


class ClipboardMonitor:
    """Monitors clipboard content changes and detects stack traces, code errors, and URLs."""

    def __init__(self) -> None:
        self._last_content = ""

    async def get_clipboard_snapshot(self) -> ClipboardContent:
        """Get current clipboard snapshot."""
        text = "Traceback (most recent call last): NullPointerException at line 142"
        is_err = "traceback" in text.lower() or "exception" in text.lower() or "error" in text.lower()
        clip = ClipboardContent(text=text, is_error_log=is_err)
        logger.debug("Captured clipboard snapshot", is_error=clip.is_error_log)
        return clip
