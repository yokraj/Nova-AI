"""Dashboard Permissions Module.

Defines role-based access control (RBAC) scopes and permission checks for
enterprise dashboard views and admin control capabilities.
"""

from typing import Final, List

# Dashboard Permission Scopes
READ_DASHBOARD_OVERVIEW: Final[str] = "dashboard:overview:read"
READ_DASHBOARD_METRICS: Final[str] = "dashboard:metrics:read"
READ_DASHBOARD_LOGS: Final[str] = "dashboard:logs:read"
MANAGE_DASHBOARD_CONFIG: Final[str] = "dashboard:config:write"

# Security enforcement helpers are imported from app.security.permissions

