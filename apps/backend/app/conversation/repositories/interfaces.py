"""Repository abstraction contracts for the Conversation bounded context data layer.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import uuid

from app.database.models import Conversation, Message, Attachment


class IConversationRepository(ABC):
    """Abstraction contract managing Conversation entities storage transactions."""

    @abstractmethod
    async def create(self, user_id: uuid.UUID, title: str) -> Conversation:
        """Initializes and returns a new Conversation entity."""
        pass

    @abstractmethod
    async def get_by_id(self, conversation_id: uuid.UUID) -> Optional[Conversation]:
        """Retrieves a conversation record by unique ID."""
        pass

    @abstractmethod
    async def list_by_user(self, user_id: uuid.UUID) -> List[Conversation]:
        """Retrieves all active conversation records associated with user."""
        pass

    @abstractmethod
    async def rename(self, conversation_id: uuid.UUID, title: str) -> Optional[Conversation]:
        """Renames conversation header title."""
        pass

    @abstractmethod
    async def archive(self, conversation_id: uuid.UUID) -> Optional[Conversation]:
        """Archives a conversation thread."""
        pass

    @abstractmethod
    async def delete(self, conversation_id: uuid.UUID) -> bool:
        """Soft-deletes a conversation thread by setting status to DELETED."""
        pass

    @abstractmethod
    async def restore(self, conversation_id: uuid.UUID) -> Optional[Conversation]:
        """Restores an archived or soft-deleted conversation back to ACTIVE status."""
        pass

    @abstractmethod
    async def exists(self, conversation_id: uuid.UUID) -> bool:
        """Verifies if conversation thread exists in storage."""
        pass

    @abstractmethod
    async def count_by_user(self, user_id: uuid.UUID) -> int:
        """Counts total active conversations for a user."""
        pass

    @abstractmethod
    async def paginate(self, user_id: uuid.UUID, limit: int, offset: int) -> List[Conversation]:
        """Retrieves paginated active conversations thread records."""
        pass

    @abstractmethod
    async def save(self, conversation: Conversation) -> Conversation:
        """Persists or updates a conversation entity in storage."""
        pass


class IMessageRepository(ABC):
    """Abstraction contract managing Message entities storage transactions."""

    @abstractmethod
    async def create(
        self, conversation_id: uuid.UUID, role: str, content: str, token_count: int = 0
    ) -> Message:
        """Initializes and appends a new Message entity."""
        pass

    @abstractmethod
    async def get_by_id(self, message_id: uuid.UUID) -> Optional[Message]:
        """Retrieves a message record by unique ID."""
        pass

    @abstractmethod
    async def list_by_conversation(self, conversation_id: uuid.UUID) -> List[Message]:
        """Retrieves all message records associated with conversation thread."""
        pass

    @abstractmethod
    async def delete(self, message_id: uuid.UUID) -> bool:
        """Permanently deletes a message record by ID."""
        pass

    @abstractmethod
    async def count_messages(self, conversation_id: uuid.UUID) -> int:
        """Counts total messages within a conversation thread."""
        pass

    @abstractmethod
    async def latest_message(self, conversation_id: uuid.UUID) -> Optional[Message]:
        """Retrieves the latest appended message in thread."""
        pass

    @abstractmethod
    async def paginate(self, conversation_id: uuid.UUID, limit: int, offset: int) -> List[Message]:
        """Retrieves paginated messages thread records."""
        pass

    @abstractmethod
    async def save(self, message: Message) -> Message:
        """Persists or updates a message entity in storage."""
        pass


class IAttachmentRepository(ABC):
    """Abstraction contract managing Attachment entities storage transactions."""

    @abstractmethod
    async def create(
        self, message_id: uuid.UUID, name: str, type: str, url: str, size: int
    ) -> Attachment:
        """Initializes and returns a new Attachment entity."""
        pass

    @abstractmethod
    async def get_by_id(self, attachment_id: uuid.UUID) -> Optional[Attachment]:
        """Retrieves an attachment record by unique ID."""
        pass

    @abstractmethod
    async def list_by_message(self, message_id: uuid.UUID) -> List[Attachment]:
        """Retrieves all attachment records associated with message."""
        pass

    @abstractmethod
    async def delete(self, attachment_id: uuid.UUID) -> bool:
        """Permanently deletes an attachment record by ID."""
        pass

    @abstractmethod
    async def delete_by_message(self, message_id: uuid.UUID) -> int:
        """Deletes all attachments associated with message."""
        pass

    @abstractmethod
    async def save(self, attachment: Attachment) -> Attachment:
        """Persists or updates an attachment entity in storage."""
        pass
