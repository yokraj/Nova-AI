"""Router placeholders interface definitions for the Identity APIs.

Declares routes interfaces namespaces for signup, log, profiles, and tokens.
"""

from fastapi import APIRouter

from app.identity.schemas.domain_schemas import (
    LoginRequest,
    LoginResponse,
    ProfileResponse,
    RegisterRequest,
    RegisterResponse,
    UpdateProfileRequest,
)

auth_placeholder_router = APIRouter(prefix="/auth", tags=["Auth Placeholders"])
user_placeholder_router = APIRouter(prefix="/users", tags=["Users Placeholders"])


@auth_placeholder_router.post("/register", response_model=RegisterResponse)
async def register_placeholder(request: RegisterRequest) -> RegisterResponse:
    """Placeholder endpoint for account signup/registration."""
    raise NotImplementedError("Concrete registration handler not implemented.")


@auth_placeholder_router.post("/login", response_model=LoginResponse)
async def login_placeholder(request: LoginRequest) -> LoginResponse:
    """Placeholder endpoint for account authentication/login."""
    raise NotImplementedError("Concrete login handler not implemented.")


@auth_placeholder_router.post("/refresh", response_model=LoginResponse)
async def refresh_placeholder() -> LoginResponse:
    """Placeholder endpoint for token refresh/rotation."""
    raise NotImplementedError("Concrete token rotation handler not implemented.")


@auth_placeholder_router.post("/logout")
async def logout_placeholder() -> None:
    """Placeholder endpoint for session termination/logout."""
    raise NotImplementedError("Concrete logout handler not implemented.")


@user_placeholder_router.get("/me", response_model=ProfileResponse)
async def get_profile_placeholder() -> ProfileResponse:
    """Placeholder endpoint for user profile fetching."""
    raise NotImplementedError("Concrete profile retrieval handler not implemented.")


@user_placeholder_router.put("/me", response_model=ProfileResponse)
async def update_profile_placeholder(
    request: UpdateProfileRequest,
) -> ProfileResponse:
    """Placeholder endpoint for user profile modification."""
    raise NotImplementedError("Concrete profile update handler not implemented.")
