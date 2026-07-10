"""Service abstraction contracts for the Conversation bounded context.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import uuid

from app.database.models import Conversation, Message
from app.conversation.application.commands import (
    CreateConversationCommand,
    SendMessageCommand,
)
from app.conversation.schemas.domain_schemas import (
    ConversationResponse,
    ConversationSummary,
    MessageResponse,
)


class IConversationService(ABC):
    """Abstraction contract for orchestrating conversation thread business operations."""

    @abstractmethod
    async def create_conversation(
        self, command: CreateConversationCommand
    ) -> ConversationResponse:
        """Initializes a new conversation thread."""
        pass

    @abstractmethod
    async def send_message(self, command: SendMessageCommand) -> MessageResponse:
        """Sends and appends a message within a conversation."""
        pass

    @abstractmethod
    async def rename_conversation(
        self, conversation_id: uuid.UUID, title: str
    ) -> ConversationResponse:
        """Renames a conversation thread's title."""
        pass

    @abstractmethod
    async def archive_conversation(
        self, conversation_id: uuid.UUID
    ) -> ConversationResponse:
        """Archives a conversation thread."""
        pass

    @abstractmethod
    async def delete_conversation(self, conversation_id: uuid.UUID) -> None:
        """Permanently deletes a conversation thread."""
        pass


class IContextWindowService(ABC):
    """Abstraction contract managing AI model context window truncation optimization operations."""

    @abstractmethod
    async def optimize_context(
        self, messages: List[Message], model_name: str, token_limit: int
    ) -> List[Message]:
        """Filters/Truncates messages thread history to fit within a model's token limits."""
        pass

    @abstractmethod
    async def get_remaining_budget(
        self, messages: List[Message], token_limit: int
    ) -> int:
        """Calculates unused tokens allocation budget remaining."""
        pass


class ITokenCounter(ABC):
    """Abstraction contract calculating LLM token counts for content elements."""

    @abstractmethod
    def count_tokens(self, text: str, model_name: str) -> int:
        """Calculates token counts for raw text string using a target model's tokenizer."""
        pass

    @abstractmethod
    def count_message_tokens(self, message: Dict[str, Any], model_name: str) -> int:
        """Calculates token counts for structured message objects (role/content metadata)."""
        pass
