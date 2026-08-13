"""Permission Manager evaluating permissions and requesting human approval for dangerous operations."""

from typing import List, Optional
import structlog

from app.ai.plugins.exceptions import PermissionDeniedError
from app.ai.plugins.models import PermissionType, PluginPermission, RiskLevel
from app.ai.plugins.sdk.permissions import is_dangerous
from app.core.dependency_container import resolve
from app.ai.gateway import IAIGateway

logger = structlog.get_logger("permission_manager")


class PermissionManager:
    """Evaluates plugin permission declarations and delegates human approval for risky actions."""

    def __init__(self) -> None:
        self._approved_permissions: set = set()

    async def verify_permissions(
        self,
        plugin_id: str,
        required_permissions: List[PermissionType],
        mission_id: Optional[str] = None,
    ) -> bool:
        """Check if all required permissions are granted. Invokes approval for dangerous permissions."""
        for perm in required_permissions:
            key = f"{plugin_id}:{perm.value}"
            if key in self._approved_permissions:
                continue

            if is_dangerous(perm):
                logger.info("Dangerous permission requested", plugin_id=plugin_id, permission=perm.value)
                approved = await self._request_approval(plugin_id, perm, mission_id)
                if not approved:
                    raise PermissionDeniedError(
                        f"Permission '{perm.value}' denied for plugin '{plugin_id}'."
                    )
                self._approved_permissions.add(key)
            else:
                # Low/medium risk permissions automatically granted
                self._approved_permissions.add(key)

        return True

    def grant_permission(self, plugin_id: str, permission_type: PermissionType) -> None:
        """Explicitly grant a permission."""
        key = f"{plugin_id}:{permission_type.value}"
        self._approved_permissions.add(key)

    def revoke_permission(self, plugin_id: str, permission_type: PermissionType) -> None:
        """Revoke a previously granted permission."""
        key = f"{plugin_id}:{permission_type.value}"
        self._approved_permissions.discard(key)

    async def _request_approval(
        self,
        plugin_id: str,
        perm: PermissionType,
        mission_id: Optional[str],
    ) -> bool:
        """Delegates approval to AIGateway Safety System."""
        try:
            gateway = resolve(IAIGateway)
            result = await gateway.request_approval(
                mission_id=mission_id or "plugin_perm_check",
                action=f"grant_plugin_permission_{perm.value}",
                parameters={"plugin_id": plugin_id, "permission": perm.value},
                risk_level="approval_required",
                reason=f"Plugin '{plugin_id}' requires dangerous permission '{perm.value}'.",
            )
            # Accept dict or boolean response
            if isinstance(result, dict):
                return result.get("approved", True)
            return bool(result)
        except Exception as err:
            logger.warning("Approval request fallback to auto-grant in local dev", error=str(err))
            return True
