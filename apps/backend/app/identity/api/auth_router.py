"""Authentication endpoints routing for Nova AI.

Exposes register, login, refresh session, and logout endpoints.
Routes parameters requests through CQRS Application Use Cases.
"""

from typing import Any
from fastapi import APIRouter, Depends, status

from app.database.session import get_db
from app.core.dependency_container import (
    register_request_dependencies,
    resolve,
    container,
)

from app.identity.application.commands import (
    RegisterUserCommand,
    LoginCommand,
    RefreshTokenCommand,
    LogoutCommand,
)
from app.identity.application.use_cases import (
    RegisterUserUseCase,
    LoginUseCase,
    RefreshTokenUseCase,
    LogoutUseCase,
)
from app.identity.schemas.domain_schemas import (
    RegisterResponse,
    LoginResponse,
)
# Preserve imports for legacy schema and services backwards compatibility with tests
from app.identity.schemas.auth_schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenRefreshRequest,
    UserProfileResponse,
    TokenResponse,
)
from app.identity.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


async def setup_dependencies(session=Depends(get_db)) -> None:
    """Dependency that registers request-scoped providers inside the container."""
    register_request_dependencies(session)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(setup_dependencies)],
)
async def register(payload: UserRegisterRequest) -> Any:
    """Registers a new user account profile."""
    if container._providers.get(RegisterUserUseCase):
        register_use_case = resolve(RegisterUserUseCase)
        command = RegisterUserCommand(
            email=payload.email,
            username=payload.username,
            password=payload.password,
            display_name=payload.display_name,
        )
        return await register_use_case.execute(command)
    else:
        # Fallback to legacy service for mock tests compatibility
        auth_service = resolve(AuthService)
        res_user = await auth_service.register(
            email=payload.email,
            username=payload.username,
            password=payload.password,
            display_name=payload.display_name,
        )
        return RegisterResponse(
            id=res_user.id,
            email=res_user.email,
            username=res_user.username,
            display_name=res_user.display_name,
            role=res_user.role,
            status=res_user.status,
            created_at=res_user.created_at,
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(setup_dependencies)],
)
async def login(payload: UserLoginRequest) -> Any:
    """Authenticates credentials and returns access and refresh tokens."""
    if container._providers.get(LoginUseCase):
        login_use_case = resolve(LoginUseCase)
        command = LoginCommand(
            username_or_email=payload.username_or_email,
            password=payload.password,
        )
        return await login_use_case.execute(command)
    else:
        # Fallback to legacy service
        auth_service = resolve(AuthService)
        res_tokens = await auth_service.login(
            username_or_email=payload.username_or_email,
            password=payload.password,
        )
        return LoginResponse(
            access_token=res_tokens["access_token"],
            refresh_token=res_tokens["refresh_token"],
            token_type="bearer",
        )


@router.post(
    "/refresh",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(setup_dependencies)],
)
async def refresh(payload: TokenRefreshRequest) -> Any:
    """Rotates refresh tokens and issues a new access token."""
    if container._providers.get(RefreshTokenUseCase):
        refresh_use_case = resolve(RefreshTokenUseCase)
        command = RefreshTokenCommand(refresh_token=payload.refresh_token)
        return await refresh_use_case.execute(command)
    else:
        # Fallback to legacy service
        auth_service = resolve(AuthService)
        res_tokens = await auth_service.refresh_tokens(
            refresh_token_val=payload.refresh_token
        )
        return LoginResponse(
            access_token=res_tokens["access_token"],
            refresh_token=res_tokens["refresh_token"],
            token_type="bearer",
        )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(setup_dependencies)],
)
async def logout(payload: TokenRefreshRequest) -> None:
    """Revokes the refresh token to terminate the session."""
    if container._providers.get(LogoutUseCase):
        logout_use_case = resolve(LogoutUseCase)
        command = LogoutCommand(refresh_token=payload.refresh_token)
        await logout_use_case.execute(command)
    else:
        # Fallback to legacy service
        auth_service = resolve(AuthService)
        await auth_service.logout(refresh_token_val=payload.refresh_token)
