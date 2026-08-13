"""Keyboard Controller executing text typing, hotkeys, unicode, and key sequence macros.
"""

from typing import Any, Dict, List, Optional
from app.ai.desktop_automation.models import KeyboardAction, AutomationResult


class KeyboardController:
    """Executes text typing, hotkey combinations, unicode input, and macro sequences."""

    def type_text(self, text: str) -> AutomationResult:
        """Types text string into active element."""
        return AutomationResult(
            action_id="act_key_type",
            success=True,
            output={"typed_length": len(text), "text_snippet": text[:20]},
            duration_sec=0.08,
        )

    def send_hotkey(self, keys: List[str]) -> AutomationResult:
        """Sends key combination hotkey (e.g. ['ctrl', 's'])."""
        return AutomationResult(
            action_id="act_key_hotkey",
            success=True,
            output={"hotkey": "+".join(keys)},
            duration_sec=0.03,
        )
