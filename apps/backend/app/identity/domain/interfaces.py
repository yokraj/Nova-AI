"""Domain entity interfaces for the Nova AI Identity bounded context.

Establishes structural blueprints for users profiles, sessions, refresh tokens,
and preference entities.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
import uuid


class IUser(ABC):
    """Contract defining core User profile entity attributes."""

    @property
    @abstractmethod
    def id(self) -> uuid.UUID:
        """Unique UUID primary identifier."""
        pass

    @property
    @abstractmethod
    def email(self) -> str:
        """Email address of the user."""
        pass

    @property
    @abstractmethod
    def username(self) -> str:
        """Unique login username."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> Optional[str]:
        """Optional user profile display name."""
        pass

    @property
    @abstractmethod
    def status(self) -> str:
        """User account status (e.g. 'active', 'inactive')."""
        pass

    @property
    @abstractmethod
    def role(self) -> str:
        """User access role (e.g. 'admin', 'user')."""
        pass


class ISession(ABC):
    """Contract defining User login sessions attributes."""

    @property
    @abstractmethod
    def id(self) -> uuid.UUID:
        """Unique session UUID primary identifier."""
        pass

    @property
    @abstractmethod
    def user_id(self) -> uuid.UUID:
        """Owner User UUID reference."""
        pass

    @property
    @abstractmethod
    def token(self) -> str:
        """Session token string value."""
        pass

    @property
    @abstractmethod
    def expires_at(self) -> datetime:
        """Expiration datetime in UTC."""
        pass


class IRefreshToken(ABC):
    """Contract defining rotatable RefreshToken attributes."""

    @property
    @abstractmethod
    def id(self) -> uuid.UUID:
        """Unique token UUID primary identifier."""
        pass

    @property
    @abstractmethod
    def user_id(self) -> uuid.UUID:
        """Owner User UUID reference."""
        pass

    @property
    @abstractmethod
    def token(self) -> str:
        """Refresh token string value."""
        pass

    @property
    @abstractmethod
    def is_revoked(self) -> bool:
        """Revocation flag indicating token validity."""
        pass

    @property
    @abstractmethod
    def expires_at(self) -> datetime:
        """Expiration datetime in UTC."""
        pass


class IUserPreference(ABC):
    """Contract defining key-value settings preferences profiles."""

    @property
    @abstractmethod
    def id(self) -> uuid.UUID:
        """Unique preference UUID identifier."""
        pass

    @property
    @abstractmethod
    def user_id(self) -> uuid.UUID:
        """Owner User UUID reference."""
        pass

    @property
    @abstractmethod
    def key(self) -> str:
        """Key descriptor of preference."""
        pass

    @property
    @abstractmethod
    def value(self) -> str:
        """Value string mapping of preference."""
        pass
