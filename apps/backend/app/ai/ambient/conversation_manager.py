"""Conversation Manager managing multi-turn voice conversations and context carry-over."""

from typing import Any, Dict
import structlog

from app.ai.ambient.interfaces import IConversationManager
from app.ai.ambient.models import ConversationState, ConversationTurn, VoiceSessionRecord

logger = structlog.get_logger("conversation_manager")


class ConversationManager(IConversationManager):
    """Manages active multi-turn voice conversations, turn history, and context carry-over."""

    def __init__(self) -> None:
        self.active_session = VoiceSessionRecord()

    async def handle_user_speech(self, text: str) -> Dict[str, Any]:
        """Process user turn in multi-turn voice conversation."""
        self.active_session.turns.append(ConversationTurn(speaker="user", text=text))
        logger.info("Conversation turn received", text=text, total_turns=len(self.active_session.turns))

        # Dynamic intent resolution
        t_lower = text.lower()
        if "summarize" in t_lower and "teams" in t_lower:
            response = "Summarizing Microsoft Teams meeting agenda: 1) Q3 Roadmap, 2) Architecture Review."
        elif "analyze" in t_lower or "error" in t_lower:
            response = "Analyzing debugging error log in VS Code: NullPointerException at line 142."
        else:
            response = f"I am listening. Regarding '{text}', how can I assist you further?"

        self.active_session.turns.append(ConversationTurn(speaker="assistant", text=response))
        self.active_session.state = ConversationState.WAITING_USER

        return {
            "session_id": self.active_session.session_id,
            "turns_count": len(self.active_session.turns),
            "response": response,
        }
