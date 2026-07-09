"""Service interfaces contracts for the Nova AI Identity bounded context.

Declares password hashing utilities, cryptographic token handlers, and core workflow managers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import uuid

from app.database.models import User


class IPasswordHasher(ABC):
    """Abstraction contract managing security cryptography passwords hashing."""

    @abstractmethod
    def hash(self, password: str) -> str:
        """Computes secure bcrypt hash of password.

        Args:
            password: Plain-text password.

        Returns:
            The secure hashed string value.
        """
        pass

    @abstractmethod
    def verify(self, password: str, hashed_password: str) -> bool:
        """Verifies plain-text password matches hash.

        Args:
            password: Plain-text password.
            hashed_password: Hashed password.

        Returns:
            True if matched; False otherwise.
        """
        pass


class ITokenService(ABC):
    """Abstraction contract managing JWT token validation and payloads generation."""

    @abstractmethod
    def generate_tokens(self, user: User) -> Dict[str, str]:
        """Generates access and refresh token keys.

        Args:
            user: The User instance.

        Returns:
            A dictionary containing generated access and refresh tokens.
        """
        pass

    @abstractmethod
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decodes JWT claims details.

        Args:
            token: Access token string.

        Returns:
            Decoded claims payload dictionary.
        """
        pass


class IIdentityService(ABC):
    """High-level orchestration contract coordinating user account workflows."""

    @abstractmethod
    async def register(
        self, email: str, username: str, password: str, display_name: Optional[str] = None
    ) -> User:
        """Coordinates user account profile registrations.

        Args:
            email: Email address.
            username: Display username.
            password: Hashing verification password.
            display_name: Optional display name.

        Returns:
            The registered User entity.
        """
        pass

    @abstractmethod
    async def login(
        self, username_or_email: str, password: str
    ) -> Dict[str, str]:
        """Validates credentials and generates access/refresh tokens.

        Args:
            username_or_email: Credentials descriptor.
            password: Plain password verification.

        Returns:
            Dictionary containing tokens.
        """
        pass

    @abstractmethod
    async def refresh_tokens(self, refresh_token_val: str) -> Dict[str, str]:
        """Rotates tokens family using a refresh token key.

        Args:
            refresh_token_val: Active refresh token.

        Returns:
            Dictionary containing new rotated access/refresh tokens.
        """
        pass

    @abstractmethod
    async def logout(self, refresh_token_val: str) -> None:
        """Invalidates user refresh token session.

        Args:
            refresh_token_val: Invalidation token.
        """
        pass


from typing import Any
