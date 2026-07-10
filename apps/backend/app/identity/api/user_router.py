"""User profile and record queries routing for Nova AI.

Exposes endpoints to view and update user profile.
Routes parameters requests through CQRS Application Use Cases.
"""

from typing import Any, List
import uuid
from fastapi import APIRouter, Depends, status

from app.database.session import get_db
from app.core.dependency_container import (
    register_request_dependencies,
    resolve,
    container,
)
from app.identity.infrastructure.rbac import PermissionChecker, get_current_user_claims
from app.identity.schemas.domain_schemas import ProfileResponse, UpdateProfileRequest
from app.identity.application.queries import GetProfileQuery
from app.identity.application.commands import UpdateProfileCommand
from app.identity.application.use_cases import GetProfileUseCase, UpdateProfileUseCase

# Preserve legacy imports for backwards compatibility with tests
from app.identity.schemas.auth_schemas import UserProfileResponse
from app.identity.services.user_service import UserService
from app.identity.infrastructure.user_repository import UserRepository

router = APIRouter(tags=["users"])


async def setup_dependencies(session=Depends(get_db)) -> None:
    """Dependency that registers request-scoped providers inside the container."""
    register_request_dependencies(session)


@router.get(
    "/profile",
    response_model=ProfileResponse,
    dependencies=[Depends(setup_dependencies)],
)
async def get_profile(claims: dict = Depends(get_current_user_claims)) -> Any:
    """Fetches the profile details of the authenticated user session."""
    user_id = uuid.UUID(claims["user_id"])
    if container._providers.get(GetProfileUseCase):
        get_profile_use_case = resolve(GetProfileUseCase)
        query = GetProfileQuery(user_id=user_id)
        return await get_profile_use_case.execute(query)
    else:
        # Fallback to legacy service for mock tests compatibility
        user_service: UserService = resolve(UserService)
        res_user = await user_service.get_user_profile(user_id)
        return ProfileResponse(
            id=res_user.id,
            email=res_user.email,
            username=res_user.username,
            display_name=res_user.display_name,
            avatar_url=res_user.avatar_url,
            role=res_user.role,
            status=res_user.status,
            created_at=res_user.created_at,
            updated_at=res_user.updated_at,
        )


@router.patch(
    "/profile",
    response_model=ProfileResponse,
    dependencies=[Depends(setup_dependencies)],
)
async def update_profile(
    payload: UpdateProfileRequest,
    claims: dict = Depends(get_current_user_claims),
) -> Any:
    """Updates user display name and/or avatar properties."""
    user_id = uuid.UUID(claims["user_id"])
    update_profile_use_case = resolve(UpdateProfileUseCase)
    command = UpdateProfileCommand(
        user_id=user_id,
        display_name=payload.display_name,
        avatar_url=payload.avatar_url,
    )
    return await update_profile_use_case.execute(command)


@router.get(
    "/users",
    response_model=List[ProfileResponse],
    dependencies=[
        Depends(setup_dependencies),
        Depends(PermissionChecker("read:users")),
    ],
)
async def list_users() -> List[Any]:
    """Retrieves all registered user profiles in the system (Admin only)."""
    user_repo: UserRepository = resolve(UserRepository)
    users = await user_repo.list()
    # Map entities to DTO responses
    return [
        ProfileResponse(
            id=u.id,
            email=u.email,
            username=u.username,
            display_name=u.display_name,
            avatar_url=u.avatar_url,
            role=u.role,
            status=u.status,
            created_at=u.created_at,
            updated_at=u.updated_at,
        )
        for u in users
    ]
