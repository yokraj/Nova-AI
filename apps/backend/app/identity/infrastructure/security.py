"""Security and Cryptography tools for the Nova AI Identity platform.

Implements password hashing (bcrypt), JWT generation/decoding,
and secure hex token generators.
"""

from datetime import datetime, timedelta, timezone
import secrets
from typing import Any, Dict, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# CryptContext configured with bcrypt backend scheme
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Global JWT constants
JWT_SECRET_KEY = "NOVA_AI_SECRET_KEY_PLACEHOLDER"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    """Hashes a plaintext password string using bcrypt.

    Args:
        password: The plaintext password string.

    Returns:
        The bcrypt-hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a hashed bcrypt representation.

    Args:
        plain_password: The plaintext password.
        hashed_password: The bcrypt-hashed password to check.

    Returns:
        True if the password matches; False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


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
    to_encode = payload.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT access token claim.

    Args:
        token: The encoded token string.

    Returns:
        The decoded dictionary claim payload.

    Raises:
        JWTError: If token signature check or parsing fails.
    """
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])


def generate_refresh_token() -> str:
    """Generates a cryptographically secure random hexadecimal refresh token."""
    return secrets.token_hex(32)
