"""Permission Manager tracking dynamic permission scopes.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from app.ai.safety.models import UserConsent

class PermissionManager:
    """Stores temporary and persistent permissions grants."""

    def __init__(self) -> None:
        self._grants: Dict[str, UserConsent] = {}

    def grant_permission(self, scope: str, seconds: int = 3600) -> str:
        """Grants temporary permission for a scope."""
        p_id = f"perm_{scope}"
        expiration = datetime.utcnow() + timedelta(seconds=seconds)
        self._grants[p_id] = UserConsent(
            permission_id=p_id,
            scope=scope,
            granted=True,
            expiration=expiration,
            session_scoped=True
        )
        return p_id

    def check_permission(self, scope: str) -> bool:
        """Returns True if the permission scope is active and not expired."""
        p_id = f"perm_{scope}"
        consent = self._grants.get(p_id)
        if not consent or not consent.granted:
            return False

        if consent.expiration and consent.expiration < datetime.utcnow():
            consent.granted = False  # Expired
            return False

        return True
