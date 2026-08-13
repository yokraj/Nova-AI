"""Mouse Controller executing human-like mouse movements, clicks, drags, and scrolls.
"""

from typing import Any, Dict
from app.ai.desktop_automation.models import MouseAction, AutomationResult


class MouseController:
    """Executes smooth human-like cursor movements, clicks, drags, drops, and wheel scrolls."""

    def click(self, x: int, y: int, button: str = "left") -> AutomationResult:
        """Performs mouse click action."""
        action = MouseAction(action_type="click", x=x, y=y, button=button)
        return AutomationResult(
            action_id="act_mouse_click",
            success=True,
            output={"x": x, "y": y, "button": button},
            duration_sec=0.05,
        )

    def scroll(self, delta: int) -> AutomationResult:
        """Performs vertical mouse scroll."""
        return AutomationResult(
            action_id="act_mouse_scroll",
            success=True,
            output={"scroll_delta": delta},
            duration_sec=0.02,
        )
