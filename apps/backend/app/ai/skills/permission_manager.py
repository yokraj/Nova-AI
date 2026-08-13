"""Security Permission Manager verifying access control and sensitive permission prompts.
"""

from typing import List
from app.ai.skills.interfaces import IPermissionManager
from app.ai.skills.models import PermissionType


class PermissionManager(IPermissionManager):
    """Enforces access control policies across Filesystem, Network, Desktop, Camera, and Payments."""

    def check_permissions(self, required: List[PermissionType], granted: List[PermissionType]) -> bool:
        """Verifies if required permissions are included in granted permissions.

        Args:
            required: List of required PermissionType enums.
            granted: List of granted PermissionType enums.

        Returns:
            True if all required permissions are granted.
        """
        for req in required:
            if req not in granted:
                return False
        return True

    def requires_sensitive_approval(self, permissions: List[PermissionType]) -> bool:
        """Returns True if any permission scope requires human approval prompt."""
        sensitive_scopes = {
            PermissionType.PAYMENTS,
            PermissionType.SYSTEM_SETTINGS,
            PermissionType.FILESYSTEM,
            PermissionType.CAMERA,
        }
        return any(p in sensitive_scopes for p in permissions)
