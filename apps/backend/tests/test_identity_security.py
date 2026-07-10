"""Unit tests for the Identity Security Layer.

Verifies password hashing contexts, JWT claim validation algorithms,
and refresh token rotations with reuse family invalidations.
"""

from unittest.mock import AsyncMock
import uuid
import pytest

from app.database.models import RefreshToken
from app.identity.repositories.interfaces import IRefreshTokenRepository
from app.identity.services.exceptions import (
    ExpiredTokenError,
    InvalidTokenError,
    TokenReuseDetectedError,
)
from app.identity.services.jwt_service import JwtService
from app.identity.services.password_hasher import PasswordHasher
from app.identity.services.security_facade import SecurityService


def test_password_hasher() -> None:
    """Verifies hash generation and verification checks."""
    hasher = PasswordHasher(work_factor=4)  # Small rounds factor for fast test
    password = "super-secret-password"

    hashed = hasher.hash(password)
    assert hashed != password
    assert hasher.verify(password, hashed) is True
    assert hasher.verify("wrong-password", hashed) is False
    assert hasher.needs_rehash(hashed) is False


def test_jwt_service() -> None:
    """Verifies JWT validation claims, issuer, aud, and signatures verification."""
    jwt_serv = JwtService(
        secret_key="test-secret-key-signing",
        algorithm="HS256",
        issuer="test-issuer",
        audience="test-audience",
        access_token_expire_minutes=5,
    )
    subject = "user-1234"

    token = jwt_serv.create_access_token(subject, {"custom_field": "test"})
    claims = jwt_serv.verify_access_token(token)

    assert claims["sub"] == subject
    assert claims["iss"] == "test-issuer"
    assert claims["aud"] == "test-audience"
    assert claims["custom_field"] == "test"
    assert "jti" in claims
    assert "exp" in claims


def test_jwt_service_expired_token() -> None:
    """Verifies expired signatures trigger ExpiredTokenError."""
    jwt_serv = JwtService(
        secret_key="test-secret-key-signing",
        access_token_expire_minutes=-10,  # Pre-expired
    )
    token = jwt_serv.create_access_token("user-1")

    with pytest.raises(ExpiredTokenError):
        jwt_serv.verify_access_token(token)


@pytest.mark.anyio
async def test_security_facade_and_rotation_flow() -> None:
    """Verifies refresh token family allocations and reuse protection hooks."""
    token_repo = AsyncMock(spec=IRefreshTokenRepository)
    hasher = PasswordHasher(work_factor=4)
    jwt_serv = JwtService(secret_key="test-secret")
    security = SecurityService(hasher, jwt_serv, token_repo)

    user_id = uuid.uuid4()

    # 1. Create refresh token record
    record = await security.create_refresh_token_record(user_id)
    assert record.user_id == user_id
    assert len(record.token) > 0
    assert record.is_revoked is False
    token_repo.save.assert_called_once_with(record)
    token_repo.save.reset_mock()

    # 2. Successfully rotate token
    token_repo.get_by_token.return_value = record
    rotated = await security.rotate_refresh_token(record.token)

    assert record.is_revoked is True
    assert rotated.user_id == user_id
    assert rotated.token != record.token
    assert token_repo.save.call_count == 2
    token_repo.save.reset_mock()

    with pytest.raises(TokenReuseDetectedError):
        await security.rotate_refresh_token(record.token)

    token_repo.revoke_family.assert_called_once_with(user_id)
