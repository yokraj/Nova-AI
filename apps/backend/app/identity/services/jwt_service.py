"""JSON Web Token (JWT) encoding and validation service.

Generates and decodes access and refresh token objects containing standards claims.
"""

from datetime import UTC, datetime, timedelta
from typing import Any, Dict, Optional
from jose import JWTError, jwt
import uuid

from app.identity.services.exceptions import ExpiredTokenError, InvalidTokenError
from app.identity.services.interfaces import ITokenService


class JwtService(ITokenService):
    """Cryptographic JWT Service implementing ITokenService interface."""

    def __init__(
        self,
        secret_key: str = "NOVA_AI_SECRET_KEY_PLACEHOLDER",
        algorithm: str = "HS256",
        issuer: str = "nova-ai",
        audience: str = "nova-ai-clients",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
    ) -> None:
        """Initializes the JwtService.

        Args:
            secret_key: The cryptographic signing key.
            algorithm: Target hashing algorithm (e.g. HS256).
            issuer: Issuer claim (iss).
            audience: Target audience claim (aud).
            access_token_expire_minutes: Expiration duration minutes.
            refresh_token_expire_days: Expiration duration days.
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.issuer = issuer
        self.audience = audience
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(
        self, subject: str, extra_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generates a secure JSON Web Token (JWT) access token.

        Args:
            subject: Unique subject claim (sub), maps to User ID.
            extra_claims: Extra claim payload definitions.

        Returns:
            The encoded JWT token string.
        """
        now = datetime.now(UTC)
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        claims = {
            "iss": self.issuer,
            "aud": self.audience,
            "sub": subject,
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "jti": str(uuid.uuid4()),
        }
        if extra_claims:
            claims.update(extra_claims)
        return jwt.encode(claims, self.secret_key, algorithm=self.algorithm)

    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Decodes and validates an access token.

        Args:
            token: The encoded token string.

        Returns:
            The decoded dictionary claim payload.

        Raises:
            ExpiredTokenError: If token expired signature checks fail.
            InvalidTokenError: If token signature or claims verification fails.
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer,
            )
            return payload
        except jwt.ExpiredSignatureError as error:
            raise ExpiredTokenError("Access token signature has expired.") from error
        except JWTError as error:
            raise InvalidTokenError("Access token signature is invalid.") from error

    def create_refresh_token(
        self, subject: str, extra_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generates a secure JSON Web Token (JWT) refresh token.

        Args:
            subject: Unique subject claim (sub), maps to User ID.
            extra_claims: Extra claim payload definitions.

        Returns:
            The encoded JWT token string.
        """
        now = datetime.now(UTC)
        expire = now + timedelta(days=self.refresh_token_expire_days)
        claims = {
            "iss": self.issuer,
            "aud": self.audience,
            "sub": subject,
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "jti": str(uuid.uuid4()),
        }
        if extra_claims:
            claims.update(extra_claims)
        return jwt.encode(claims, self.secret_key, algorithm=self.algorithm)

    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """Decodes and validates a refresh token.

        Args:
            token: The encoded token string.

        Returns:
            The decoded dictionary claim payload.

        Raises:
            ExpiredTokenError: If refresh token expired checks fail.
            InvalidTokenError: If signature verification checks fail.
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer,
            )
            return payload
        except jwt.ExpiredSignatureError as error:
            raise ExpiredTokenError("Refresh token signature has expired.") from error
        except JWTError as error:
            raise InvalidTokenError("Refresh token signature is invalid.") from error

    def generate_tokens(self, user: Any) -> Dict[str, str]:
        """Generates access and refresh tokens dict payload.

        Args:
            user: User entity mappings.

        Returns:
            A dictionary containing access_token and refresh_token keys.
        """
        sub = str(user.id)
        extra = {"email": user.email, "role": user.role}
        return {
            "access_token": self.create_access_token(sub, extra),
            "refresh_token": self.create_refresh_token(sub),
        }

    def decode_token(self, token: str) -> Dict[str, Any]:
        """Exposes token decoding capability for validation.

        Args:
            token: Access token string.

        Returns:
            Decoded claims payload dictionary.
        """
        return self.verify_access_token(token)
