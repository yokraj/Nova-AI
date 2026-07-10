"""Concrete implementation of the Attachment repository using SQLAlchemy.
"""

from typing import List, Optional
import uuid
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Attachment
from app.conversation.repositories.interfaces import IAttachmentRepository


class AttachmentRepository(IAttachmentRepository):
    """SQLAlchemy concrete database adapter for managing attachments data."""

    def __init__(self, session: AsyncSession) -> None:
        """Initializes the AttachmentRepository.

        Args:
            session: Active SQLAlchemy AsyncSession.
        """
        self.session = session

    async def create(
        self, message_id: uuid.UUID, name: str, type: str, url: str, size: int
    ) -> Attachment:
        """Initializes and returns a new Attachment entity.

        Args:
            message_id: Owner Message UUID.
            name: File upload filename.
            type: AttachmentType file format descriptor.
            url: Public download url link.
            size: Size in bytes.

        Returns:
            The newly created Attachment entity.
        """
        attachment = Attachment(
            message_id=message_id,
            name=name,
            type=type,
            url=url,
            size=size,
        )
        self.session.add(attachment)
        return attachment

    async def get_by_id(self, attachment_id: uuid.UUID) -> Optional[Attachment]:
        """Retrieves an attachment record by unique ID.

        Args:
            attachment_id: Unique Attachment UUID.

        Returns:
            The Attachment instance or None.
        """
        stmt = select(Attachment).where(Attachment.id == attachment_id)
        result = await self.session.execute(stmt)
        return result.scalar_or_none()

    async def list_by_message(self, message_id: uuid.UUID) -> List[Attachment]:
        """Retrieves all attachment records associated with message.

        Args:
            message_id: Owner Message UUID.

        Returns:
            List of attachments associated with message.
        """
        stmt = select(Attachment).where(Attachment.message_id == message_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, attachment_id: uuid.UUID) -> bool:
        """Permanently deletes an attachment record by ID.

        Args:
            attachment_id: Unique Attachment UUID.

        Returns:
            True if attachment existed and was deleted; False otherwise.
        """
        attachment = await self.get_by_id(attachment_id)
        if attachment:
            await self.session.delete(attachment)
            return True
        return False

    async def delete_by_message(self, message_id: uuid.UUID) -> int:
        """Deletes all attachments associated with message.

        Args:
            message_id: Owner Message UUID.

        Returns:
            Number of deleted attachment rows.
        """
        stmt = delete(Attachment).where(Attachment.message_id == message_id)
        result = await self.session.execute(stmt)
        return result.rowcount

    async def save(self, attachment: Attachment) -> Attachment:
        """Persists or updates an attachment entity in storage.

        Args:
            attachment: The Attachment instance.

        Returns:
            The persisted Attachment instance.
        """
        if attachment not in self.session:
            self.session.add(attachment)
        return attachment
