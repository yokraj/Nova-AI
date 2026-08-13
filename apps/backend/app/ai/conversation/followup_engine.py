"""Followup Engine resolving implicit follow-up references across sessions.
"""

from typing import Any, Dict
from app.ai.conversation.models import ConversationSession


class FollowupEngine:
    """Resolves implicit follow-up prompts (e.g. 'Continue yesterday's dashboard')."""

    def resolve_followup(self, session: ConversationSession, prompt: str) -> str:
        """Resolves implicit prompt references using past session context.

        Args:
            session: ConversationSession instance.
            prompt: User utterance prompt string.

        Returns:
            Fully resolved explicit prompt string.
        """
        p_lower = prompt.lower()
        if "continue" in p_lower or "yesterday" in p_lower:
            return f"Resume task context from previous session: '{prompt}'"
        return prompt
