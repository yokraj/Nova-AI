"""Role Manager defining Admin, Lead, Developer, Researcher, Viewer roles and custom permissions.
"""

from typing import List
from app.ai.workspace.models import MemberRole


class RoleManager:
    """Manages workspace member roles and permission matrix mapping."""

    def get_role_permissions(self, role: MemberRole) -> List[str]:
        """Returns list of allowed permission action strings for role."""
        if role == MemberRole.ADMIN:
            return ["create", "read", "update", "delete", "manage_members", "execute_remote"]
        elif role in (MemberRole.LEAD, MemberRole.DEVELOPER):
            return ["create", "read", "update", "execute_remote"]
        return ["read"]
