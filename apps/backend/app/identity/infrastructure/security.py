"""Security and Cryptography tools for the Nova AI Identity platform.

Implements password hashing (bcrypt), JWT generation/decoding,
and secure hex token generators. Redirects to modernized security services.
"""

from datetime import timedelta
from typing import Any, Dict, Optional

from app.identity.services.jwt_service import JwtService
from app.identity.services.password_hasher import PasswordHasher

# Global config variables preserved for imports compatibility
JWT_SECRET_KEY = "NOVA_AI_SECRET_KEY_PLACEHOLDER"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Instantiate facade services backings
_hasher = PasswordHasher()
_jwt = JwtService(
    secret_key=JWT_SECRET_KEY,
    algorithm=JWT_ALGORITHM,
    access_token_expire_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
    refresh_token_expire_days=REFRESH_TOKEN_EXPIRE_DAYS,
)


def hash_password(password: str) -> str:
    """Hashes a plaintext password string using bcrypt.

    Args:
        password: The plaintext password string.

    Returns:
        The bcrypt-hashed password string.
    """
    return _hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a hashed bcrypt representation.

    Args:
        plain_password: The plaintext password.
        hashed_password: The bcrypt-hashed password to check.

    Returns:
        True if the password matches; False otherwise.
    """
    return _hasher.verify(plain_password, hashed_password)


def create_access_token(
    payload: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Generates a secure JSON Web Token (JWT) access token.

    Args:
        payload: The dictionary key-value data to bind inside the claim.
        expires_delta: Optional override duration for token expiration.

    Returns:
        The encoded string representation of the JWT access token.
    """
    sub = payload.get("sub", "")
    # Preserve extra fields in payload claims
    extra = {k: v for k, v in payload.items() if k != "sub"}

    if expires_delta:
        # If delta is provided, calculate minutes override
        mins = int(expires_delta.total_seconds() / 60)
        jwt_override = JwtService(
            secret_key=JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
            access_token_expire_minutes=mins,
        )
        return jwt_override.create_access_token(sub, extra)

    return _jwt.create_access_token(sub, extra)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT access token claim.

    Args:
        token: The encoded token string.

    Returns:
        The decoded dictionary claim payload.
    """
    from app.identity.services.exceptions import InvalidTokenError

    try:
        return _jwt.verify_access_token(token)
    except InvalidTokenError as error:
        from jose import JWTError

        # Raise JWTError for compatibility with legacy decode handlers
        raise JWTError(str(error)) from error


def generate_refresh_token() -> str:
    """Generates a cryptographically secure random hexadecimal refresh token."""
    import secrets

    return secrets.token_hex(32)
