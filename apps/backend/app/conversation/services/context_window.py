"""Trimming and budget optimization services for conversation context windows.
"""

from typing import List

from app.database.models import Message
from app.conversation.services.interfaces import IContextWindowService, ITokenCounter


class ContextWindowService(IContextWindowService):
    """Orchestrates token budgeting and content assembly for LLM context windows."""

    def __init__(self, token_counter: ITokenCounter) -> None:
        """Initializes ContextWindowService.

        Args:
            token_counter: Active token counter instance.
        """
        self.token_counter = token_counter

    async def optimize_context(
        self, messages: List[Message], model_name: str, token_limit: int
    ) -> List[Message]:
        """Trims chat message history to fit context window budget limits.

        System instructions are always preserved at the start of the thread.

        Args:
            messages: Full list of messages in thread.
            model_name: Target AI model name.
            token_limit: Maximum allowed context tokens.

        Returns:
            Optimized subset list of Messages.
        """
        system_msgs = [m for m in messages if m.role == "system"]
        chat_msgs = [m for m in messages if m.role != "system"]

        # Calculate system message tokens
        sys_tokens = sum(
            self.token_counter.count_message_tokens(
                {"role": m.role, "content": m.content}, model_name
            )
            for m in system_msgs
        )

        available_limit = token_limit - sys_tokens
        current_tokens = 0
        optimized = []

        # Consume newest messages first
        for m in reversed(chat_msgs):
            m_tokens = self.token_counter.count_message_tokens(
                {"role": m.role, "content": m.content}, model_name
            )
            if current_tokens + m_tokens <= available_limit:
                optimized.insert(0, m)
                current_tokens += m_tokens
            else:
                break

        return system_msgs + optimized

    async def get_remaining_budget(
        self, messages: List[Message], token_limit: int
    ) -> int:
        """Calculates remaining unused tokens.

        Args:
            messages: Active list of messages.
            token_limit: Maximum allowed context tokens.

        Returns:
            Remaining budget tokens.
        """
        total = sum(
            self.token_counter.count_message_tokens(
                {"role": m.role, "content": m.content}, "gpt-4"
            )
            for m in messages
        )
        return max(0, token_limit - total)
