"""Decorators for developer-friendly plugin creation."""

from typing import Any, Callable, List, Optional
from app.ai.plugins.models import CapabilityType, PermissionType, PluginCapability, PluginPermission, RiskLevel


def nova_plugin(
    name: str,
    version: str = "1.0.0",
    author: str = "Nova AI",
    description: str = "",
    permissions: Optional[List[PermissionType]] = None,
) -> Callable[[type], type]:
    """Class decorator to mark a class as a Nova Plugin."""

    def decorator(cls: type) -> type:
        cls.name = name
        cls.version = version
        cls.author = author
        cls.description = description

        # Attach permissions
        declared_perms = permissions or []
        cls_permissions = []
        for p in declared_perms:
            cls_permissions.append(
                PluginPermission(
                    permission_type=p,
                    description=f"Requires {p.value} access",
                    risk_level=RiskLevel.MEDIUM if p.value in ("browser", "file_system", "network") else RiskLevel.HIGH,
                )
            )
        cls._declared_permissions = cls_permissions
        return cls

    return decorator


def capability(
    name: str,
    description: str = "",
    capability_type: CapabilityType = CapabilityType.TOOL,
    voice_intents: Optional[List[str]] = None,
    risk_level: RiskLevel = RiskLevel.LOW,
) -> Callable[[Callable], Callable]:
    """Method decorator to register a capability on a plugin class."""

    def decorator(func: Callable) -> Callable:
        cap = PluginCapability(
            name=name,
            description=description,
            capability_type=capability_type,
            voice_intents=voice_intents or [],
            risk_level=risk_level,
        )
        setattr(func, "_nova_capability", cap)
        return func

    return decorator
