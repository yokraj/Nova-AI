"""User management business services for Nova AI.

Orchestrates profile queries and validations.
"""

from typing import Optional
import uuid

from app.identity.domain.user import User
from app.identity.infrastructure.user_repository import UserRepository
from app.services.base import BaseService


class UserService(BaseService):
    """Business service managing profile fetching and operations on User records."""

    def __init__(self, user_repository: UserRepository) -> None:
        """Initializes the UserService with target repositories.

        Args:
            user_repository: Concrete UserRepository instance.
        """
        super().__init__()
        self.user_repo = user_repository

    async def get_user_profile(self, user_id: uuid.UUID) -> Optional[User]:
        """Fetches the profile user entity details for a target ID.

        Args:
            user_id: The unique user UUID.

        Returns:
            The matched User entity or None.
        """
        self.log_info("fetching_user_profile", user_id=str(user_id))
        user = await self.user_repo.get(user_id)
        if not user:
            self.log_error("user_profile_not_found", user_id=str(user_id))
        return user
