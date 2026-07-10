"""Integration tests for the Identity API router.

Verifies FastAPI HTTP responses status codes, validation payloads, Bearer JWT
headers, and OpenAPI metadata generation.
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
import uuid
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.core.dependency_container import container
from app.database.models import RefreshToken, User
from app.database.session import get_db
from app.identity.api.auth_router import setup_dependencies as auth_setup
from app.identity.api.user_router import setup_dependencies as user_setup
from app.identity.application.use_cases import (
    GetProfileUseCase,
    LoginUseCase,
    LogoutUseCase,
    RefreshTokenUseCase,
    RegisterUserUseCase,
    UpdateProfileUseCase,
)
from app.identity.schemas.domain_schemas import (
    LoginResponse,
    ProfileResponse,
    RegisterResponse,
)
from app.identity.services.exceptions import (
    InvalidCredentialsError,
    InvalidTokenError,
)
from app.main import app


# Override database to bypass dynamic pool setups
async def mock_get_db() -> AsyncMock:
    """Mock database dependency yielding a mock session."""
    yield AsyncMock()


async def mock_setup_dependencies() -> None:
    """Mock setup to bypass container overrides in tests."""
    pass


app.dependency_overrides[get_db] = mock_get_db
app.dependency_overrides[auth_setup] = mock_setup_dependencies
app.dependency_overrides[user_setup] = mock_setup_dependencies

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_container_fixture() -> None:
    """Clears dependency injection registries before and after execution."""
    container.clear()
    yield
    container.clear()


def test_openapi_documentation_structure() -> None:
    """Verifies that OpenAPI documentation contains identity REST endpoints."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == status.HTTP_200_OK

    schema = response.json()
    paths = schema["paths"]

    assert "/api/v1/auth/register" in paths
    assert "/api/v1/auth/login" in paths
    assert "/api/v1/auth/refresh" in paths
    assert "/api/v1/auth/logout" in paths
    assert "/api/v1/profile" in paths


def test_api_register_endpoint_success() -> None:
    """Verifies that POST /auth/register success case routes to use case."""
    mock_uc = AsyncMock(spec=RegisterUserUseCase)
    mock_uc.execute.return_value = RegisterResponse(
        id=uuid.uuid4(),
        email="api@example.com",
        username="apiuser",
        display_name="API User",
        role="user",
        status="active",
        created_at=datetime.now(UTC),
    )
    container.register(RegisterUserUseCase, lambda: mock_uc)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "api@example.com",
            "username": "apiuser",
            "password": "secure_password_123",
            "display_name": "API User",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "api@example.com"
    assert data["username"] == "apiuser"


def test_api_register_endpoint_conflict() -> None:
    """Verifies that duplicate register requests trigger HTTP 409 Conflict status."""
    mock_uc = AsyncMock(spec=RegisterUserUseCase)
    mock_uc.execute.side_effect = InvalidCredentialsError(
        "Email address is already registered."
    )
    container.register(RegisterUserUseCase, lambda: mock_uc)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "api@example.com",
            "username": "apiuser",
            "password": "secure_password_123",
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    assert "already registered" in data["message"]


def test_api_login_endpoint_success() -> None:
    """Verifies that POST /auth/login returns access and refresh tokens."""
    mock_uc = AsyncMock(spec=LoginUseCase)
    mock_uc.execute.return_value = LoginResponse(
        access_token="jwt-access-token-val",
        refresh_token="secure-random-refresh-token",
        token_type="bearer",
    )
    container.register(LoginUseCase, lambda: mock_uc)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "username_or_email": "api@example.com",
            "password": "secure_password_123",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["access_token"] == "jwt-access-token-val"
    assert data["refresh_token"] == "secure-random-refresh-token"


def test_api_refresh_endpoint_success() -> None:
    """Verifies that POST /auth/refresh rotates tokens successfully."""
    mock_uc = AsyncMock(spec=RefreshTokenUseCase)
    mock_uc.execute.return_value = LoginResponse(
        access_token="new-jwt-access-token",
        refresh_token="new-secure-refresh-token",
        token_type="bearer",
    )
    container.register(RefreshTokenUseCase, lambda: mock_uc)

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "old-refresh-token"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["access_token"] == "new-jwt-access-token"
    assert data["refresh_token"] == "new-secure-refresh-token"


def test_api_logout_endpoint_success() -> None:
    """Verifies that POST /auth/logout invalidates token with HTTP 204."""
    mock_uc = AsyncMock(spec=LogoutUseCase)
    container.register(LogoutUseCase, lambda: mock_uc)

    response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": "old-refresh-token"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_uc.execute.assert_called_once()
