"""User profile and record queries routing for Nova AI.

Exposes endpoints to view current profile and list system users (Admin restricted).
"""

from typing import Any, List
import uuid
from fastapi import APIRouter, Depends

from app.database.session import get_db
from app.core.dependency_container import register_request_dependencies, resolve
from app.identity.infrastructure.rbac import PermissionChecker, get_current_user_claims
from app.identity.infrastructure.user_repository import UserRepository
from app.identity.schemas.auth_schemas import UserProfileResponse
from app.identity.services.user_service import UserService

router = APIRouter(tags=["users"])


async def setup_dependencies(session=Depends(get_db)) -> None:
    """Dependency that registers request-scoped providers inside the container."""
    register_request_dependencies(session)


@router.get(
    "/profile",
    response_model=UserProfileResponse,
    dependencies=[Depends(setup_dependencies)],
)
async def get_profile(claims: dict = Depends(get_current_user_claims)) -> Any:
    """Fetches the profile details of the authenticated user session."""
    user_service: UserService = resolve(UserService)
    # Parse subject claim back to UUID
    user_id = uuid.UUID(claims["user_id"])
    return await user_service.get_user_profile(user_id)


@router.get(
    "/users",
    response_model=List[UserProfileResponse],
    dependencies=[Depends(setup_dependencies), Depends(PermissionChecker("read:users"))],
)
async def list_users() -> List[Any]:
    """Retrieves all registered user profiles in the system (Admin only)."""
    user_repo: UserRepository = resolve(UserRepository)
    return await user_repo.list()
