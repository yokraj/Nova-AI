"""Conversation Learning Engine learning user communication preferences and technical depth.
"""

from typing import Any, Dict


class ConversationLearningEngine:
    """Learns user preferred explanation depth, terminology, favorite IDE, and communication style."""

    def __init__(self) -> None:
        self._learned_preferences: Dict[str, Any] = {
            "preferred_depth": "high",
            "favorite_ide": "VS Code",
            "communication_style": "concise_technical",
        }

    def learn_from_turn(self, text: str) -> None:
        """Updates learned user preferences from turn utterance.

        Args:
            text: Utterance text.
        """
        if "simple" in text.lower() or "explain like i'm 5" in text.lower():
            self._learned_preferences["preferred_depth"] = "low"
        elif "deep dive" in text.lower() or "architecture" in text.lower():
            self._learned_preferences["preferred_depth"] = "high"

    def get_preferences(self) -> Dict[str, Any]:
        """Returns snapshot of learned user preferences."""
        return self._learned_preferences
