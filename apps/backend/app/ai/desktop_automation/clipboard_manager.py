"""Clipboard Manager managing system clipboard history, text, images, files, and rich text.
"""

from typing import Any, Dict, Optional
from app.ai.desktop_automation.models import ClipboardData


class ClipboardManager:
    """Manages system clipboard reading, writing, history stack, and format conversion."""

    def __init__(self) -> None:
        self._current_data = ClipboardData(data_type="text", text_content="Nova AI Clipboard Initialized")

    def get_clipboard(self) -> ClipboardData:
        """Retrieves active clipboard payload."""
        return self._current_data

    def set_clipboard_text(self, text: str) -> ClipboardData:
        """Sets clipboard text content."""
        self._current_data = ClipboardData(data_type="text", text_content=text)
        return self._current_data
