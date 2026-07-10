"""Concrete implementation of the Message repository using SQLAlchemy.
"""

from typing import List, Optional
import uuid
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Message
from app.conversation.repositories.interfaces import IMessageRepository


class MessageRepository(IMessageRepository):
    """SQLAlchemy concrete database adapter for managing messages thread data."""

    def __init__(self, session: AsyncSession) -> None:
        """Initializes the MessageRepository.

        Args:
            session: Active SQLAlchemy AsyncSession.
        """
        self.session = session

    async def create(
        self, conversation_id: uuid.UUID, role: str, content: str, token_count: int = 0
    ) -> Message:
        """Initializes and appends a new Message entity.

        Args:
            conversation_id: Associated Conversation UUID.
            role: Sender actor role tags (user, assistant, system).
            content: Main text content string.
            token_count: Hashing calculation tokenizer counts metrics.

        Returns:
            The newly created Message entity.
        """
        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            token_count=token_count,
        )
        self.session.add(msg)
        return msg

    async def get_by_id(self, message_id: uuid.UUID) -> Optional[Message]:
        """Retrieves a message record by unique ID.

        Args:
            message_id: Unique Message UUID.

        Returns:
            The Message instance or None.
        """
        stmt = select(Message).where(Message.id == message_id)
        result = await self.session.execute(stmt)
        return result.scalar_or_none()

    async def list_by_conversation(self, conversation_id: uuid.UUID) -> List[Message]:
        """Retrieves all message records associated with conversation thread.

        Args:
            conversation_id: Associated Conversation UUID.

        Returns:
            List of messages ordered chronologically.
        """
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, message_id: uuid.UUID) -> bool:
        """Permanently deletes a message record by ID.

        Args:
            message_id: Unique Message UUID.

        Returns:
            True if message existed and was deleted; False otherwise.
        """
        msg = await self.get_by_id(message_id)
        if msg:
            await self.session.delete(msg)
            return True
        return False

    async def count_messages(self, conversation_id: uuid.UUID) -> int:
        """Counts total messages within a conversation thread.

        Args:
            conversation_id: Associated Conversation UUID.

        Returns:
            Count number integer.
        """
        stmt = (
            select(func.count())
            .select_from(Message)
            .where(Message.conversation_id == conversation_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def latest_message(self, conversation_id: uuid.UUID) -> Optional[Message]:
        """Retrieves the latest appended message in thread.

        Args:
            conversation_id: Associated Conversation UUID.

        Returns:
            The latest Message instance or None.
        """
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_or_none()

    async def paginate(self, conversation_id: uuid.UUID, limit: int, offset: int) -> List[Message]:
        """Retrieves paginated messages thread records.

        Args:
            conversation_id: Associated Conversation UUID.
            limit: Limit pagination offset size.
            offset: Skip elements index.

        Returns:
            List of messages.
        """
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def save(self, message: Message) -> Message:
        """Persists or updates a message entity in storage.

        Args:
            message: The Message instance.

        Returns:
            The persisted Message instance.
        """
        if message not in self.session:
            self.session.add(message)
        return message
