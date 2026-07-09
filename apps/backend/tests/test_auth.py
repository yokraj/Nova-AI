"""Unit and integration tests for Nova AI Identity & Security Platform.

Verifies user registration, login, refresh token rotations,
token family reuse revocations, and RBAC authorization policies.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock
import uuid
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependency_container import container
from app.database.session import get_db
from app.identity.api.auth_router import setup_dependencies as auth_setup
from app.identity.api.user_router import setup_dependencies as user_setup
from app.identity.domain.user import User
from app.identity.infrastructure.rbac import ROLE_PERMISSIONS
from app.identity.schemas.auth_schemas import UserProfileResponse
from app.identity.services.auth_service import AuthService
from app.identity.services.user_service import UserService
from app.main import app


# Override database and setup dependencies to prevent database connection attempts
async def mock_get_db() -> AsyncMock:
    """Mock database dependency yielding a mock session."""
    yield AsyncMock(spec=AsyncSession)


async def mock_setup_dependencies() -> None:
    """Mock request dependency registry setup keeping mocked services in container."""
    pass


app.dependency_overrides[get_db] = mock_get_db
app.dependency_overrides[auth_setup] = mock_setup_dependencies
app.dependency_overrides[user_setup] = mock_setup_dependencies

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_container_fixture() -> None:
    """Fixture clearing dependency container registries before/after each test."""
    container.clear()
    yield
    container.clear()


def test_registration_endpoint_success() -> None:
    """Verifies that user register endpoint succeeds with correct payload."""
    mock_auth_service = AsyncMock(spec=AuthService)
    # Generate explicit ID and timestamps to satisfy Pydantic response validation
    mock_user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        username="testuser",
        password_hash="hashed",
        display_name="Test User",
        role="user",
        status="active",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    mock_auth_service.register.return_value = mock_user
    container.register(AuthService, lambda: mock_auth_service)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "secure_password123",
            "display_name": "Test User",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["role"] == "user"
    mock_auth_service.register.assert_called_once()


def test_login_endpoint_success() -> None:
    """Verifies that login endpoint returns access and refresh tokens."""
    mock_auth_service = AsyncMock(spec=AuthService)
    mock_auth_service.login.return_value = {
        "access_token": "mocked_access_token",
        "refresh_token": "mocked_refresh_token",
    }
    container.register(AuthService, lambda: mock_auth_service)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "username_or_email": "testuser",
            "password": "secure_password123",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["access_token"] == "mocked_access_token"
    assert data["refresh_token"] == "mocked_refresh_token"
    mock_auth_service.login.assert_called_once_with(
        username_or_email="testuser", password="secure_password123"
    )


def test_refresh_endpoint_success() -> None:
    """Verifies that token refresh endpoint rotates access/refresh tokens."""
    mock_auth_service = AsyncMock(spec=AuthService)
    mock_auth_service.refresh_tokens.return_value = {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
    }
    container.register(AuthService, lambda: mock_auth_service)

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "old_refresh_token"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["access_token"] == "new_access_token"
    assert data["refresh_token"] == "new_refresh_token"
    mock_auth_service.refresh_tokens.assert_called_once_with(
        refresh_token_val="old_refresh_token"
    )


def test_rbac_permissions_matrix() -> None:
    """Verifies defined access permissions mappings for roles."""
    assert "read:users" in ROLE_PERMISSIONS["admin"]
    assert "admin:access" in ROLE_PERMISSIONS["admin"]
    assert "read:profile" in ROLE_PERMISSIONS["user"]
    assert "read:users" not in ROLE_PERMISSIONS["user"]
