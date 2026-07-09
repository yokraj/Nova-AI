"""Session model query repository for Nova AI.

Exposes operations to filter, manage, and delete Session records in the database.
"""

from datetime import datetime, timezone
from typing import List, Optional
import uuid
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Session
from app.repositories.base import BaseRepository
from app.identity.repositories.interfaces import ISessionRepository


class SessionRepository(BaseRepository[Session], ISessionRepository):
    """Concrete repository mapping customized queries for the Session model."""

    def __init__(self, session: AsyncSession) -> None:
        """Initializes the SessionRepository.

        Args:
            session: The active SQLAlchemy AsyncSession instance.
        """
        super().__init__(Session, session)

    async def create(self, session_record: Session) -> Session:
        """Saves a new Session record instance into the database session tracker.

        Args:
            session_record: The Session instance to add.

        Returns:
            The added Session instance.
        """
        self.session.add(session_record)
        return session_record

    async def get_by_id(self, session_id: uuid.UUID) -> Optional[Session]:
        """Queries the database for a single Session matching the target session_id.

        Args:
            session_id: Unique identifier.

        Returns:
            The matched Session instance, or None if not found.
        """
        return await self.session.get(self.model, session_id)

    async def get_by_token(self, token: str) -> Optional[Session]:
        """Queries the database for a single Session matching the token value.

        Args:
            token: The bearer validation token.

        Returns:
            The matched Session instance, or None if not found.
        """
        statement = select(self.model).where(self.model.token == token)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_active_sessions(self, user_id: uuid.UUID) -> List[Session]:
        """Queries database for active (unexpired) sessions associated with a user ID.

        Args:
            user_id: Target user identifier.

        Returns:
            A list of active Session records.
        """
        now = datetime.now(timezone.utc)
        statement = select(self.model).where(
            self.model.user_id == user_id, self.model.expires_at > now
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def revoke(self, session_id: uuid.UUID) -> Optional[Session]:
        """Revokes (deletes) a session.

        Args:
            session_id: Unique session identifier.

        Returns:
            The revoked Session instance, or None if not found.
        """
        session_record = await self.get_by_id(session_id)
        if session_record:
            await self.session.delete(session_record)
        return session_record

    async def delete_expired(self) -> None:
        """Deletes expired sessions from database storage."""
        now = datetime.now(timezone.utc)
        statement = delete(self.model).where(self.model.expires_at < now)
        await self.session.execute(statement)

    async def save(self, session_record: Session) -> Session:
        """Persists or updates a Session entity.

        Args:
            session_record: The Session instance.

        Returns:
            The persisted Session instance.
        """
        return await self.create(session_record)

    async def delete(self, session_id: uuid.UUID) -> None:
        """Removes a Session from storage.

        Args:
            session_id: Unique identifier.
        """
        await self.revoke(session_id)
