"""Permission definitions and helpers for the Plugin SDK."""

from typing import Dict
from app.ai.plugins.models import PermissionType, RiskLevel


PERMISSION_RISK_MAP: Dict[PermissionType, RiskLevel] = {
    PermissionType.BROWSER: RiskLevel.MEDIUM,
    PermissionType.DESKTOP: RiskLevel.HIGH,
    PermissionType.FILE_SYSTEM: RiskLevel.MEDIUM,
    PermissionType.CAMERA: RiskLevel.HIGH,
    PermissionType.MICROPHONE: RiskLevel.HIGH,
    PermissionType.NETWORK: RiskLevel.MEDIUM,
    PermissionType.EMAIL: RiskLevel.HIGH,
    PermissionType.CALENDAR: RiskLevel.LOW,
    PermissionType.CLIPBOARD: RiskLevel.LOW,
    PermissionType.NOTIFICATIONS: RiskLevel.LOW,
    PermissionType.TERMINAL: RiskLevel.CRITICAL,
}


def is_dangerous(permission_type: PermissionType) -> bool:
    """Determine if a permission requires human approval."""
    risk = PERMISSION_RISK_MAP.get(permission_type, RiskLevel.LOW)
    return risk in (RiskLevel.HIGH, RiskLevel.CRITICAL)
