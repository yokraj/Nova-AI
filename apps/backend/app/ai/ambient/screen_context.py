"""Screen Context capturing visual UI state and screen changes."""

from typing import Any, Dict
import structlog

logger = structlog.get_logger("screen_context")


class ScreenContext:
    """Captures visual screen OCR and UI change context."""

    async def get_screen_summary(self) -> Dict[str, Any]:
        """Get visual screen summary."""
        return {"detected_text": "Incomplete registration form detected", "has_form": True}
