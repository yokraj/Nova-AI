"""Permission Manager checking fine-grained role permissions for workspace actions.
"""

from app.ai.workspace.models import MemberRole
from app.ai.workspace.role_manager import RoleManager


class PermissionManager:
    """Enforces fine-grained permission checks for workspace resource access."""

    def __init__(self) -> None:
        self.role_manager = RoleManager()

    def check_permission(self, role: MemberRole, action: str) -> bool:
        """Returns True if action is allowed for given MemberRole."""
        allowed_actions = self.role_manager.get_role_permissions(role)
        return action in allowed_actions
