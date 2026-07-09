"""Authentication endpoints routing for Nova AI.

Exposes register, login, refresh session, and logout endpoints.
"""

from typing import Any
from fastapi import APIRouter, Depends, status

from app.database.session import get_db
from app.core.dependency_container import register_request_dependencies, resolve
from app.identity.schemas.auth_schemas import (
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserProfileResponse,
)
from app.identity.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


async def setup_dependencies(session=Depends(get_db)) -> None:
    """Dependency that registers request-scoped providers inside the container."""
    register_request_dependencies(session)


@router.post(
    "/register",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(setup_dependencies)],
)
async def register(payload: UserRegisterRequest) -> Any:
    """Registers a new user account profile."""
    auth_service: AuthService = resolve(AuthService)
    return await auth_service.register(
        email=payload.email,
        username=payload.username,
        password=payload.password,
        display_name=payload.display_name,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(setup_dependencies)],
)
async def login(payload: UserLoginRequest) -> Any:
    """Authenticates credentials and returns access and refresh tokens."""
    auth_service: AuthService = resolve(AuthService)
    return await auth_service.login(
        username_or_email=payload.username_or_email, password=payload.password
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(setup_dependencies)],
)
async def refresh(payload: TokenRefreshRequest) -> Any:
    """Rotates refresh tokens and issues a new access token."""
    auth_service: AuthService = resolve(AuthService)
    return await auth_service.refresh_tokens(
        refresh_token_val=payload.refresh_token
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(setup_dependencies)],
)
async def logout(payload: TokenRefreshRequest) -> None:
    """Revokes the refresh token to terminate the session."""
    auth_service: AuthService = resolve(AuthService)
    await auth_service.logout(refresh_token_val=payload.refresh_token)
