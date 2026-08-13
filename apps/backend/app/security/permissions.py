"""Permission Verification Helpers Module.

Extends existing project RBAC definitions with helper functions for verifying
dashboard, analytics, notification, and system administrative claims.
"""

from typing import Any, Dict, List, Optional, Set
import structlog

from app.identity.infrastructure.rbac import ROLE_PERMISSIONS, PermissionChecker

logger = structlog.get_logger(__name__)

# Extended Permission Matrix
EXTENDED_ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "admin": {
        "dashboard:read",
        "dashboard:write",
        "dashboard:admin",
        "analytics:read",
        "notifications:read",
        "notifications:write",
        "system:read",
        "system:admin",
    },
    "operator": {
        "dashboard:read",
        "dashboard:write",
        "analytics:read",
        "notifications:read",
        "notifications:write",
        "system:read",
    },
    "user": {
        "dashboard:read",
        "analytics:read",
        "notifications:read",
        "system:read",
    },
    "viewer": {
        "dashboard:read",
        "system:read",
    },
}


def get_user_permissions(role: str) -> Set[str]:
    """Returns combined RBAC permissions set for role."""
    base_perms: Set[str] = ROLE_PERMISSIONS.get(role, set())
    ext_perms: Set[str] = EXTENDED_ROLE_PERMISSIONS.get(role, set())
    return base_perms.union(ext_perms)


def has_permission(role: str, required_permission: str) -> bool:
    """Checks if role possesses required permission."""
    perms = get_user_permissions(role)
    if "admin:access" in perms or "dashboard:admin" in perms:
        return True
    return required_permission in perms


def check_dashboard_read(role: str) -> bool:
    return has_permission(role, "dashboard:read")


def check_dashboard_write(role: str) -> bool:
    return has_permission(role, "dashboard:write")


def check_dashboard_admin(role: str) -> bool:
    return has_permission(role, "dashboard:admin")


def check_analytics_read(role: str) -> bool:
    return has_permission(role, "analytics:read")


def check_notifications_read(role: str) -> bool:
    return has_permission(role, "notifications:read")


def check_notifications_write(role: str) -> bool:
    return has_permission(role, "notifications:write")


def check_system_read(role: str) -> bool:
    return has_permission(role, "system:read")


def check_system_admin(role: str) -> bool:
    return has_permission(role, "system:admin")
