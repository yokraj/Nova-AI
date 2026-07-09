"""User model query repository for Nova AI.

Exposes operations to query, filter, and manage User records in the database.
"""

from typing import Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.repositories.base import BaseRepository
from app.identity.repositories.interfaces import IUserRepository


class UserRepository(BaseRepository[User], IUserRepository):
    """Concrete repository mapping customized queries for the User model."""

    def __init__(self, session: AsyncSession) -> None:
        """Initializes the UserRepository.

        Args:
            session: The active SQLAlchemy AsyncSession instance.
        """
        super().__init__(User, session)

    async def create(self, user: User) -> User:
        """Saves a new User record instance into the database session tracker.

        Args:
            user: The User instance to add.

        Returns:
            The added User instance.
        """
        self.session.add(user)
        return user

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Queries the database for a single User matching the target user_id.

        Args:
            user_id: Unique identifier.

        Returns:
            The matched User instance, or None if not found.
        """
        return await self.session.get(self.model, user_id)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Queries the database for a single User matching the target email.

        Args:
            email: The target email query string.

        Returns:
            The matched User instance, or None if not found.
        """
        statement = select(self.model).where(self.model.email == email)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Queries the database for a single User matching the target username.

        Args:
            username: The target username query string.

        Returns:
            The matched User instance, or None if not found.
        """
        statement = select(self.model).where(self.model.username == username)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def exists_by_email(self, email: str) -> bool:
        """Checks if a User with the given email exists in the database.

        Args:
            email: Target email address.

        Returns:
            True if exists; False otherwise.
        """
        user = await self.get_by_email(email)
        return user is not None

    async def exists_by_username(self, username: str) -> bool:
        """Checks if a User with the given username exists in the database.

        Args:
            username: Target username string.

        Returns:
            True if exists; False otherwise.
        """
        user = await self.get_by_username(username)
        return user is not None

    async def update(self, user: User) -> User:
        """Saves updates to a User record instance into the database session tracker.

        Args:
            user: The User instance.

        Returns:
            The updated User instance.
        """
        self.session.add(user)
        return user

    async def delete(self, user_id: uuid.UUID) -> Optional[User]:
        """Deletes a database record matching the user_id.

        Args:
            user_id: Unique identifier.

        Returns:
            The deleted User instance, or None if not found.
        """
        user = await self.get_by_id(user_id)
        if user:
            await self.session.delete(user)
        return user

    async def save(self, user: User) -> User:
        """Persists or updates a User entity in storage.

        Args:
            user: The User instance.

        Returns:
            The persisted User instance.
        """
        return await self.create(user)
