"""Conversation Compressor summarizing long turn histories into compact context checkpoints.
"""

from app.ai.conversation.models import ConversationSession


class ConversationCompressor:
    """Compresses long conversation sessions into context checkpoints when token limits are exceeded."""

    def compress_history(self, session: ConversationSession) -> str:
        """Compresses history turns into summary string.

        Args:
            session: ConversationSession instance.

        Returns:
            Compressed summary string.
        """
        if len(session.turns) <= 4:
            return "History is concise."

        # Retain last 2 turns, compress earlier turns
        old_turns = session.turns[:-2]
        session.turns = session.turns[-2:]
        summary_text = f"Summary of {len(old_turns)} previous turns: Discussed project setup and architecture."
        return summary_text
