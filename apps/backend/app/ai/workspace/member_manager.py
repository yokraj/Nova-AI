"""Member Manager handling user invitations, status tracking, and multi-workspace memberships.
"""

from typing import List
from app.ai.workspace.models import MemberRole, WorkspaceDefinition, WorkspaceMember


class MemberManager:
    """Manages workspace team member invitations and role assignments."""

    def add_member(self, workspace: WorkspaceDefinition, name: str, email: str, role: MemberRole = MemberRole.DEVELOPER) -> WorkspaceMember:
        """Adds member to workspace definition.

        Args:
            workspace: Target WorkspaceDefinition.
            name: Member name string.
            email: Member email address.
            role: MemberRole enum.

        Returns:
            Created WorkspaceMember instance.
        """
        member = WorkspaceMember(name=name, email=email, role=role)
        workspace.members.append(member)
        return member

    def remove_member(self, workspace: WorkspaceDefinition, member_id: str) -> bool:
        """Removes member by member_id from workspace."""
        initial = len(workspace.members)
        workspace.members = [m for m in workspace.members if m.member_id != member_id]
        return len(workspace.members) < initial
