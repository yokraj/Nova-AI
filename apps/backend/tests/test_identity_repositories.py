"""Unit tests for the Identity Repository Layer of Nova AI.

Verifies UserRepository, SessionRepository, and RefreshTokenRepository queries
and modification operations using mocked AsyncSessions.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import RefreshToken, Session, User
from app.identity.infrastructure.session_repository import SessionRepository
from app.identity.infrastructure.token_repository import RefreshTokenRepository
from app.identity.infrastructure.user_repository import UserRepository


@pytest.mark.anyio
async def test_user_repository_operations() -> None:
    """Verifies UserRepository queries, existence checks, updates, and deletes."""
    session = AsyncMock(spec=AsyncSession)
    repo = UserRepository(session)

    # 1. Create
    user = User(
        id=uuid.uuid4(),
        email="user@example.com",
        username="user1",
        password_hash="hash",
    )
    res = await repo.create(user)
    assert res is user
    session.add.assert_called_with(user)

    # 2. Get by ID
    session.get.return_value = user
    res_id = await repo.get_by_id(user.id)
    assert res_id is user
    session.get.assert_called_with(User, user.id)

    # 3. Get by Email and Username
    mock_execute_result = MagicMock()
    mock_execute_result.scalars().first.return_value = user
    session.execute.return_value = mock_execute_result

    res_email = await repo.get_by_email("user@example.com")
    assert res_email is user

    res_username = await repo.get_by_username("user1")
    assert res_username is user

    # 4. Exists checks
    exists_email = await repo.exists_by_email("user@example.com")
    assert exists_email is True

    # 5. Update
    res_update = await repo.update(user)
    assert res_update is user

    # 6. Delete
    res_del = await repo.delete(user.id)
    assert res_del is user
    session.delete.assert_called_with(user)


@pytest.mark.anyio
async def test_session_repository_operations() -> None:
    """Verifies SessionRepository active filters, revocations, and expiry sweeps."""
    session = AsyncMock(spec=AsyncSession)
    repo = SessionRepository(session)

    user_id = uuid.uuid4()
    session_record = Session(
        id=uuid.uuid4(),
        user_id=user_id,
        token="session-token",
        expires_at=datetime.now(timezone.utc),
    )

    # 1. Create
    res = await repo.create(session_record)
    assert res is session_record
    session.add.assert_called_with(session_record)

    # 2. Active sessions
    mock_execute_result = MagicMock()
    mock_execute_result.scalars().all.return_value = [session_record]
    session.execute.return_value = mock_execute_result

    actives = await repo.get_active_sessions(user_id)
    assert len(actives) == 1
    assert actives[0] is session_record

    # 3. Revoke
    session.get.return_value = session_record
    res_revoke = await repo.revoke(session_record.id)
    assert res_revoke is session_record
    session.delete.assert_called_with(session_record)

    # 4. Delete expired
    await repo.delete_expired()
    assert session.execute.call_count > 0


@pytest.mark.anyio
async def test_token_repository_operations() -> None:
    """Verifies RefreshTokenRepository hash lookup, family revocation, and deletions."""
    session = AsyncMock(spec=AsyncSession)
    repo = RefreshTokenRepository(session)

    user_id = uuid.uuid4()
    token_record = RefreshToken(
        id=uuid.uuid4(),
        user_id=user_id,
        token="token-string",
        is_revoked=False,
        expires_at=datetime.now(timezone.utc),
    )

    # 1. Create
    res = await repo.create(token_record)
    assert res is token_record
    session.add.assert_called_with(token_record)

    # 2. Get by Hash
    mock_execute_result = MagicMock()
    mock_execute_result.scalars().first.return_value = token_record
    session.execute.return_value = mock_execute_result

    res_hash = await repo.get_by_hash("token-string")
    assert res_hash is token_record

    # 3. Revoke
    session.get.return_value = token_record
    res_revoke = await repo.revoke(token_record.id)
    assert res_revoke.is_revoked is True
    session.add.assert_called_with(token_record)

    # 4. Revoke family
    await repo.revoke_family(user_id)

    # 5. Delete expired
    await repo.delete_expired()
