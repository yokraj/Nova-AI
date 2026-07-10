"""Unit tests for the Identity Application Use Cases.

Verifies CQRS handler pipelines under mocked repositories and transactional
Unit of Work environments.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest

from app.database.models import RefreshToken, Session, User
from app.database.unit_of_work import UnitOfWork
from app.identity.application.commands import (
    LoginCommand,
    LogoutCommand,
    RefreshTokenCommand,
    RegisterUserCommand,
    UpdateProfileCommand,
)
from app.identity.application.queries import GetProfileQuery
from app.identity.application.use_cases import (
    GetProfileUseCase,
    LoginUseCase,
    LogoutUseCase,
    RefreshTokenUseCase,
    RegisterUserUseCase,
    UpdateProfileUseCase,
)
from app.identity.repositories.interfaces import (
    IRefreshTokenRepository,
    ISessionRepository,
    IUserRepository,
)
from app.identity.services.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.identity.services.password_hasher import PasswordHasher
from app.identity.services.jwt_service import JwtService
from app.identity.services.security_facade import SecurityService


@pytest.fixture
def mock_uow() -> UnitOfWork:
    """Mock database transaction UnitOfWork coordinator."""
    uow = MagicMock(spec=UnitOfWork)
    uow.session = AsyncMock()
    return uow


@pytest.mark.anyio
async def test_register_user_use_case_success(mock_uow: UnitOfWork) -> None:
    """Verifies that RegisterUserUseCase successfully registers a new user."""
    user_repo = AsyncMock(spec=IUserRepository)
    hasher = PasswordHasher(work_factor=4)

    user_repo.get_by_email.return_value = None
    user_repo.get_by_username.return_value = None

    use_case = RegisterUserUseCase(mock_uow, user_repo, hasher)
    command = RegisterUserCommand(
        email="new@example.com",
        username="newuser",
        password="password123",
        display_name="New User",
    )

    res = await use_case.execute(command)

    assert res.email == "new@example.com"
    assert res.username == "newuser"
    assert res.display_name == "New User"
    assert res.role == "user"
    assert res.status == "active"
    user_repo.save.assert_called_once()


@pytest.mark.anyio
async def test_register_user_use_case_duplicate(mock_uow: UnitOfWork) -> None:
    """Verifies duplicate email registrations trigger InvalidCredentialsError."""
    user_repo = AsyncMock(spec=IUserRepository)
    hasher = PasswordHasher(work_factor=4)

    user_repo.get_by_email.return_value = User(id=uuid.uuid4())

    use_case = RegisterUserUseCase(mock_uow, user_repo, hasher)
    command = RegisterUserCommand(
        email="duplicate@example.com",
        username="user1",
        password="password123",
    )

    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(command)


@pytest.mark.anyio
async def test_login_use_case_success(mock_uow: UnitOfWork) -> None:
    """Verifies credentials verification, token allocations, and session persistences."""
    user_repo = AsyncMock(spec=IUserRepository)
    session_repo = AsyncMock(spec=ISessionRepository)
    token_repo = AsyncMock(spec=IRefreshTokenRepository)
    security = SecurityService(
        PasswordHasher(work_factor=4), JwtService(secret_key="test-secret"), token_repo
    )

    user = User(
        id=uuid.uuid4(),
        email="user@example.com",
        username="user1",
        password_hash=security.hash_password("password123"),
        status="active",
        role="user",
    )
    user_repo.get_by_email.return_value = user

    # Configure mock JWT responses
    security.jwt.create_access_token = MagicMock(return_value="jwt-access")
    security.jwt.create_refresh_token = MagicMock(return_value="jwt-refresh")

    use_case = LoginUseCase(mock_uow, user_repo, security, session_repo)
    command = LoginCommand(
        username_or_email="user@example.com", password="password123"
    )

    res = await use_case.execute(command)

    assert res.access_token == "jwt-access"
    assert len(res.refresh_token) == 64
    session_repo.save.assert_called_once()


@pytest.mark.anyio
async def test_refresh_token_use_case(mock_uow: UnitOfWork) -> None:
    """Verifies refresh token family validation and rotation flow."""
    user_repo = AsyncMock(spec=IUserRepository)
    token_repo = AsyncMock(spec=IRefreshTokenRepository)
    security = SecurityService(
        PasswordHasher(work_factor=4), JwtService(secret_key="test-secret"), token_repo
    )

    user_id = uuid.uuid4()
    old_record = RefreshToken(
        id=uuid.uuid4(),
        user_id=user_id,
        token="old-token",
        is_revoked=False,
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )
    user = User(
        id=user_id,
        email="user@example.com",
        username="user1",
        role="user",
    )

    token_repo.get_by_token.return_value = old_record
    user_repo.get_by_id.return_value = user
    security.jwt.create_access_token = MagicMock(return_value="new-access")

    use_case = RefreshTokenUseCase(mock_uow, user_repo, security)
    command = RefreshTokenCommand(refresh_token="old-token")

    res = await use_case.execute(command)

    assert res.access_token == "new-access"
    assert old_record.is_revoked is True


@pytest.mark.anyio
async def test_logout_use_case(mock_uow: UnitOfWork) -> None:
    """Verifies token revocation upon logging out."""
    token_repo = AsyncMock(spec=IRefreshTokenRepository)
    record = RefreshToken(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        token="token-val",
        is_revoked=False,
    )
    token_repo.get_by_token.return_value = record

    use_case = LogoutUseCase(mock_uow, token_repo)
    command = LogoutCommand(refresh_token="token-val")

    await use_case.execute(command)

    assert record.is_revoked is True
    token_repo.save.assert_called_once_with(record)


@pytest.mark.anyio
async def test_get_profile_use_case() -> None:
    """Verifies user profile lookup queries."""
    user_repo = AsyncMock(spec=IUserRepository)
    user = User(
        id=uuid.uuid4(),
        email="user@example.com",
        username="user1",
        display_name="Name",
        role="user",
        status="active",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    user_repo.get_by_id.return_value = user

    use_case = GetProfileUseCase(user_repo)
    query = GetProfileQuery(user_id=user.id)

    res = await use_case.execute(query)

    assert res.id == user.id
    assert res.display_name == "Name"


@pytest.mark.anyio
async def test_update_profile_use_case(mock_uow: UnitOfWork) -> None:
    """Verifies display name and avatar updates parameters mappings."""
    user_repo = AsyncMock(spec=IUserRepository)
    user = User(
        id=uuid.uuid4(),
        email="user@example.com",
        username="user1",
        display_name="Old Name",
        avatar_url="old.png",
        role="user",
        status="active",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    user_repo.get_by_id.return_value = user

    use_case = UpdateProfileUseCase(mock_uow, user_repo)
    command = UpdateProfileCommand(
        user_id=user.id, display_name="New Name", avatar_url="new.png"
    )

    res = await use_case.execute(command)

    assert res.display_name == "New Name"
    assert res.avatar_url == "new.png"
    user_repo.save.assert_called_once_with(user)
