"""Service generating friendly titles from initial chat messages.
"""


class ConversationTitleGenerator:
    """Generates short summary titles based on the initial message text content."""

    def generate_title(self, initial_message: str) -> str:
        """Returns generated summary title or truncated prefix.

        Args:
            initial_message: Initial message text body.

        Returns:
            Summarized string title.
        """
        if not initial_message or not initial_message.strip():
            return "New Conversation"

        clean = initial_message.strip()
        if len(clean) > 30:
            return clean[:27].rstrip() + "..."
        return clean
