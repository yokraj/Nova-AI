"""Repository abstraction contracts for the Nova AI Identity data layer.

Declares methods that data store handlers must implement.
"""

from abc import ABC, abstractmethod
from typing import Optional
import uuid

from app.database.models import RefreshToken, Session, User


class IUserRepository(ABC):
    """Abstraction contract managing User entity storage transactions."""

    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Retrieves a User by their unique ID.

        Args:
            user_id: Unique identifier.

        Returns:
            The User instance, or None.
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieves a User by their email address.

        Args:
            email: Search email address.

        Returns:
            The User instance, or None.
        """
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """Retrieves a User by username.

        Args:
            username: Search username string.

        Returns:
            The User instance, or None.
        """
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        """Persists or updates a User entity in storage.

        Args:
            user: The User instance.

        Returns:
            The persisted User instance.
        """
        pass


class ISessionRepository(ABC):
    """Abstraction contract managing active user Session state transactions."""

    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[Session]:
        """Retrieves an active Session by token value.

        Args:
            token: Validation token.

        Returns:
            The Session instance, or None.
        """
        pass

    @abstractmethod
    async def save(self, session: Session) -> Session:
        """Persists or updates a Session entity.

        Args:
            session: The Session instance.

        Returns:
            The persisted Session instance.
        """
        pass

    @abstractmethod
    async def delete(self, session_id: uuid.UUID) -> None:
        """Removes a Session from storage.

        Args:
            session_id: Unique identifier.
        """
        pass


class IRefreshTokenRepository(ABC):
    """Abstraction contract managing rotatable RefreshToken family transactions."""

    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Retrieves a RefreshToken by its token value.

        Args:
            token: Search token value.

        Returns:
            The RefreshToken instance, or None.
        """
        pass

    @abstractmethod
    async def save(self, token_record: RefreshToken) -> RefreshToken:
        """Persists or updates a RefreshToken.

        Args:
            token_record: The RefreshToken instance.

        Returns:
            The persisted RefreshToken instance.
        """
        pass

    @abstractmethod
    async def revoke_family(self, user_id: uuid.UUID) -> None:
        """Revokes all active refresh tokens belonging to a user ID.

        Args:
            user_id: Owner User UUID.
        """
        pass
        # Used on reuse detections to invalidate entire token families
