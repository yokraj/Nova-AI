"""Utility functions and dynamic PEP 562 lazy module loader for app.ai.skills.
"""

import importlib
from typing import Any, Dict

_LAZY_MAP: Dict[str, str] = {
    "SkillConfiguration": "app.ai.skills.configuration",
    "SkillStatus": "app.ai.skills.models",
    "SkillCategory": "app.ai.skills.models",
    "PermissionType": "app.ai.skills.models",
    "VoiceCommandPhrase": "app.ai.skills.models",
    "SkillManifest": "app.ai.skills.models",
    "SkillMetadata": "app.ai.skills.models",
    "SkillContext": "app.ai.skills.models",
    "SkillRequest": "app.ai.skills.models",
    "SkillResponse": "app.ai.skills.models",
    "SkillTelemetry": "app.ai.skills.models",
    "SkillHealth": "app.ai.skills.models",
    "SkillMetrics": "app.ai.skills.models",
    "ISkillEngine": "app.ai.skills.interfaces",
    "ISkillRegistry": "app.ai.skills.interfaces",
    "IMarketplace": "app.ai.skills.interfaces",
    "IVoiceRegistry": "app.ai.skills.interfaces",
    "ISkillLoader": "app.ai.skills.interfaces",
    "IPermissionManager": "app.ai.skills.interfaces",
    "ISkillMemory": "app.ai.skills.interfaces",
    "ISkillManager": "app.ai.skills.interfaces",
    "SkillEngineError": "app.ai.skills.exceptions",
    "SkillNotFoundError": "app.ai.skills.exceptions",
    "PermissionDeniedError": "app.ai.skills.exceptions",
    "SkillInstallationFailedError": "app.ai.skills.exceptions",
    "InvalidManifestError": "app.ai.skills.exceptions",
    "BaseSkill": "app.ai.skills.sdk.base_skill",
    "skill_decorator": "app.ai.skills.sdk.decorators",
    "voice_command": "app.ai.skills.sdk.decorators",
    "permission_required": "app.ai.skills.sdk.decorators",
    "PermissionManager": "app.ai.skills.permission_manager",
    "VoiceRegistry": "app.ai.skills.voice_registry",
    "SkillLoader": "app.ai.skills.skill_loader",
    "SkillRegistry": "app.ai.skills.skill_registry",
    "Marketplace": "app.ai.skills.marketplace",
    "SkillMemory": "app.ai.skills.skill_memory",
    "SkillRecommendationEngine": "app.ai.skills.skill_recommendations",
    "SkillMetricsTracker": "app.ai.skills.metrics",
    "SkillHealthMonitor": "app.ai.skills.health",
    "SkillCache": "app.ai.skills.cache",
    "MockSkillProvider": "app.ai.skills.mock_provider",
    "SkillManager": "app.ai.skills.skill_manager",
    "UniversalSkillEngine": "app.ai.skills.skill_engine",
}


def lazy_import(name: str) -> Any:
    """Lazy imports a symbol based on the module map.

    Args:
        name: Name of symbol to import.

    Returns:
        The imported symbol object.
    """
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"module 'app.ai.skills' has no attribute '{name}'")


def validate_manifest(manifest_data: Dict[str, Any]) -> bool:
    """Validates raw dictionary against SkillManifest schema requirements.

    Args:
        manifest_data: Raw manifest JSON/Dict.

    Returns:
        True if valid.
    """
    return bool(manifest_data.get("skill_id") and manifest_data.get("name"))
