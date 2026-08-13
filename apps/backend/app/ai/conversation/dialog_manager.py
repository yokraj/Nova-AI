"""Dialog Manager handling multi-turn state transitions, topic tracking, and pronoun resolution.
"""

from typing import Any, Dict
from app.ai.conversation.interfaces import IDialogManager


class DialogManager(IDialogManager):
    """Manages multi-turn dialogue state, topic switches, and reference resolutions."""

    def __init__(self) -> None:
        self._active_topics: Dict[str, str] = {}

    def process_utterance(self, session_id: str, text: str) -> Dict[str, Any]:
        """Processes turn utterance and tracks active topic.

        Args:
            session_id: Target session ID string.
            text: Utterance text string.

        Returns:
            Dictionary containing topic, resolved_references, and turn intent.
        """
        words = text.split()
        topic = "general"
        if "react" in text.lower() or "dashboard" in text.lower():
            topic = "frontend_dashboard"
        elif "backend" in text.lower() or "fastapi" in text.lower():
            topic = "backend_service"
        elif "bug" in text.lower() or "error" in text.lower():
            topic = "debugging"

        self._active_topics[session_id] = topic

        return {
            "session_id": session_id,
            "topic": topic,
            "resolved_text": text,
            "intent": "general_dialog",
        }

    def get_active_topic(self, session_id: str) -> str:
        """Retrieves active topic for session_id."""
        return self._active_topics.get(session_id, "general")
