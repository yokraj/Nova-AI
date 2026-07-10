"""Security Facade orchestrator for the Nova AI platform.

Consolidates and coordinates password hashing, JWT validations,
and refresh token family rotations.
"""

from datetime import UTC, datetime, timedelta
import secrets
from typing import Any, Dict, Optional
import uuid

from app.database.models import RefreshToken
from app.identity.repositories.interfaces import IRefreshTokenRepository
from app.identity.services.exceptions import (
    ExpiredTokenError,
    InvalidTokenError,
    TokenReuseDetectedError,
)
from app.identity.services.jwt_service import JwtService
from app.identity.services.password_hasher import PasswordHasher


class SecurityService:
    """Consolidated facade service coordinating platform security controls."""

    def __init__(
        self,
        hasher: PasswordHasher,
        jwt_service: JwtService,
        token_repo: IRefreshTokenRepository,
    ) -> None:
        """Initializes the SecurityService facade.

        Args:
            hasher: PasswordHasher service instance.
            jwt_service: JwtService instance.
            token_repo: Concrete RefreshTokenRepository instance.
        """
        self.hasher = hasher
        self.jwt = jwt_service
        self.token_repo = token_repo

    def hash_password(self, password: str) -> str:
        """Hashes plaintext password.

        Args:
            password: Plaintext password.

        Returns:
            Bcrypt hashed password.
        """
        return self.hasher.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifies plaintext matches bcrypt representation.

        Args:
            plain_password: Plaintext password.
            hashed_password: Hashed password.

        Returns:
            True if matches; False otherwise.
        """
        return self.hasher.verify(plain_password, hashed_password)

    def generate_access_token(
        self, subject: str, extra: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generates a secure access token.

        Args:
            subject: Subject identifier.
            extra: Extra payload claims.

        Returns:
            Encoded JWT token.
        """
        return self.jwt.create_access_token(subject, extra)

    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Decodes and validates an access token.

        Args:
            token: Encoded token.

        Returns:
            Decoded payload claims dict.
        """
        return self.jwt.verify_access_token(token)

    def generate_secure_token(self) -> str:
        """Generates a secure cryptographically random hexadecimal token.

        Returns:
            Secure random hexadecimal string.
        """
        return secrets.token_hex(32)

    async def create_refresh_token_record(
        self, user_id: uuid.UUID
    ) -> RefreshToken:
        """Creates and persists a secure refresh token record.

        Args:
            user_id: Owner User UUID.

        Returns:
            The created RefreshToken model instance.
        """
        token_val = self.generate_secure_token()
        expires = datetime.now(UTC) + timedelta(
            days=self.jwt.refresh_token_expire_days
        )
        record = RefreshToken(
            user_id=user_id,
            token=token_val,
            is_revoked=False,
            expires_at=expires,
        )
        await self.token_repo.save(record)
        return record

    async def rotate_refresh_token(self, old_token_val: str) -> RefreshToken:
        """Rotates a refresh token, protecting against token reuse family breaches.

        Args:
            old_token_val: Active refresh token.

        Returns:
            A new rotated RefreshToken model instance.

        Raises:
            InvalidTokenError: If token does not exist in repository.
            TokenReuseDetectedError: If old token is already revoked, triggering family invalidation.
            ExpiredTokenError: If token expired checks fail.
        """
        token_record = await self.token_repo.get_by_token(old_token_val)
        if not token_record:
            raise InvalidTokenError("Refresh token not found.")

        # Token reuse detection: if old token is already revoked, invalidate family
        if token_record.is_revoked:
            await self.token_repo.revoke_family(token_record.user_id)
            raise TokenReuseDetectedError(
                "Refresh token reuse detected! Revoking entire token family."
            )

        # Lifetime verification
        if token_record.expires_at < datetime.now(UTC):
            raise ExpiredTokenError("Refresh token has expired.")

        # Revoke old token
        token_record.is_revoked = True
        await self.token_repo.save(token_record)

        # Create new rotated token
        new_record = await self.create_refresh_token_record(
            token_record.user_id
        )
        return new_record
