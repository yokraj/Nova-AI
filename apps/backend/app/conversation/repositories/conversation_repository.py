"""Concrete implementation of the Conversation repository using SQLAlchemy.
"""

from typing import List, Optional
import uuid
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Conversation
from app.database.models.enums import ConversationStatus
from app.conversation.repositories.interfaces import IConversationRepository


class ConversationRepository(IConversationRepository):
    """SQLAlchemy concrete database adapter for managing conversations thread data."""

    def __init__(self, session: AsyncSession) -> None:
        """Initializes the ConversationRepository.

        Args:
            session: Active SQLAlchemy AsyncSession.
        """
        self.session = session

    async def create(self, user_id: uuid.UUID, title: str) -> Conversation:
        """Initializes and returns a new Conversation entity.

        Args:
            user_id: Unique User UUID.
            title: Thread header title.

        Returns:
            The newly created Conversation entity.
        """
        conversation = Conversation(
            user_id=user_id,
            title=title,
            status=ConversationStatus.ACTIVE.value,
        )
        self.session.add(conversation)
        return conversation

    async def get_by_id(self, conversation_id: uuid.UUID) -> Optional[Conversation]:
        """Retrieves a conversation record by unique ID.

        Args:
            conversation_id: Unique Conversation UUID.

        Returns:
            The Conversation instance or None.
        """
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await self.session.execute(stmt)
        return result.scalar_or_none()

    async def list_by_user(self, user_id: uuid.UUID) -> List[Conversation]:
        """Retrieves all active conversation records associated with user.

        Args:
            user_id: Owner User UUID.

        Returns:
            List of active conversations.
        """
        stmt = (
            select(Conversation)
            .where(
                Conversation.user_id == user_id,
                Conversation.status != ConversationStatus.DELETED.value,
            )
            .order_by(Conversation.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def rename(self, conversation_id: uuid.UUID, title: str) -> Optional[Conversation]:
        """Renames conversation header title.

        Args:
            conversation_id: Unique Conversation UUID.
            title: New header title string.

        Returns:
            The modified Conversation or None.
        """
        conv = await self.get_by_id(conversation_id)
        if conv:
            conv.title = title
        return conv

    async def archive(self, conversation_id: uuid.UUID) -> Optional[Conversation]:
        """Archives a conversation thread.

        Args:
            conversation_id: Unique Conversation UUID.

        Returns:
            The modified Conversation or None.
        """
        conv = await self.get_by_id(conversation_id)
        if conv:
            conv.status = ConversationStatus.ARCHIVED.value
        return conv

    async def delete(self, conversation_id: uuid.UUID) -> bool:
        """Soft-deletes a conversation thread by setting status to DELETED.

        Args:
            conversation_id: Unique Conversation UUID.

        Returns:
            True if conversation existed and was soft-deleted; False otherwise.
        """
        conv = await self.get_by_id(conversation_id)
        if conv:
            conv.status = ConversationStatus.DELETED.value
            return True
        return False

    async def restore(self, conversation_id: uuid.UUID) -> Optional[Conversation]:
        """Restores an archived or soft-deleted conversation back to ACTIVE status.

        Args:
            conversation_id: Unique Conversation UUID.

        Returns:
            The modified Conversation or None.
        """
        conv = await self.get_by_id(conversation_id)
        if conv:
            conv.status = ConversationStatus.ACTIVE.value
        return conv

    async def exists(self, conversation_id: uuid.UUID) -> bool:
        """Verifies if conversation thread exists in storage.

        Args:
            conversation_id: Unique Conversation UUID.

        Returns:
            True if exists; False otherwise.
        """
        stmt = select(1).where(Conversation.id == conversation_id).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar() is not None

    async def count_by_user(self, user_id: uuid.UUID) -> int:
        """Counts total active conversations for a user.

        Args:
            user_id: Owner User UUID.

        Returns:
            Count number integer.
        """
        stmt = (
            select(func.count())
            .select_from(Conversation)
            .where(
                Conversation.user_id == user_id,
                Conversation.status != ConversationStatus.DELETED.value,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def paginate(self, user_id: uuid.UUID, limit: int, offset: int) -> List[Conversation]:
        """Retrieves paginated active conversations thread records.

        Args:
            user_id: Owner User UUID.
            limit: Pagination limit offset check count.
            offset: Skip elements index.

        Returns:
            List of active conversations.
        """
        stmt = (
            select(Conversation)
            .where(
                Conversation.user_id == user_id,
                Conversation.status != ConversationStatus.DELETED.value,
            )
            .order_by(Conversation.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def save(self, conversation: Conversation) -> Conversation:
        """Persists or updates a conversation entity in storage.

        Args:
            conversation: The Conversation instance.

        Returns:
            The persisted Conversation instance.
        """
        if conversation not in self.session:
            self.session.add(conversation)
        return conversation
