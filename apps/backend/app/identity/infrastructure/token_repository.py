"""RefreshToken model query repository for Nova AI.

Exposes operations to filter, manage, and revoke RefreshToken records in the database.
"""

from datetime import datetime, timezone
from typing import Optional
import uuid
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import RefreshToken
from app.repositories.base import BaseRepository
from app.identity.repositories.interfaces import IRefreshTokenRepository


class RefreshTokenRepository(
    BaseRepository[RefreshToken], IRefreshTokenRepository
):
    """Concrete repository mapping customized queries for the RefreshToken model."""

    def __init__(self, session: AsyncSession) -> None:
        """Initializes the RefreshTokenRepository.

        Args:
            session: The active SQLAlchemy AsyncSession instance.
        """
        super().__init__(RefreshToken, session)

    async def create(self, token_record: RefreshToken) -> RefreshToken:
        """Saves a new RefreshToken record instance into the database session tracker.

        Args:
            token_record: The RefreshToken instance to add.

        Returns:
            The added RefreshToken instance.
        """
        self.session.add(token_record)
        return token_record

    async def get_by_id(
        self, token_id: uuid.UUID
    ) -> Optional[RefreshToken]:
        """Queries the database for a single RefreshToken matching the token_id.

        Args:
            token_id: Unique identifier.

        Returns:
            The matched RefreshToken instance, or None if not found.
        """
        return await self.session.get(self.model, token_id)

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Queries the database for a single RefreshToken matching the token value.

        Args:
            token: The hexadecimal token string.

        Returns:
            The matched RefreshToken instance, or None if not found.
        """
        statement = select(self.model).where(self.model.token == token)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """Queries the database for a RefreshToken matching the hash.

        Args:
            token_hash: The target token string hash.

        Returns:
            The matched RefreshToken instance, or None if not found.
        """
        return await self.get_by_token(token_hash)

    async def revoke(self, token_id: uuid.UUID) -> Optional[RefreshToken]:
        """Revokes a refresh token.

        Args:
            token_id: Unique token identifier.

        Returns:
            The revoked RefreshToken instance, or None if not found.
        """
        token_record = await self.get_by_id(token_id)
        if token_record:
            token_record.is_revoked = True
            self.session.add(token_record)
        return token_record

    async def revoke_family(self, user_id: uuid.UUID) -> None:
        """Revokes all active refresh tokens belonging to a user ID.

        Args:
            user_id: Owner User UUID.
        """
        statement = (
            update(self.model)
            .where(self.model.user_id == user_id)
            .values(is_revoked=True)
        )
        await self.session.execute(statement)

    async def delete_expired(self) -> None:
        """Deletes expired refresh tokens from database storage."""
        now = datetime.now(timezone.utc)
        statement = delete(self.model).where(self.model.expires_at < now)
        await self.session.execute(statement)

    async def save(self, token_record: RefreshToken) -> RefreshToken:
        """Persists or updates a RefreshToken.

        Args:
            token_record: The RefreshToken instance.

        Returns:
            The persisted RefreshToken instance.
        """
        return await self.create(token_record)

    async def revoke_user_tokens(self, user_id: uuid.UUID) -> None:
        """Revokes all active refresh tokens linked to a user.

        Args:
            user_id: Owner User UUID.
        """
        await self.revoke_family(user_id)
