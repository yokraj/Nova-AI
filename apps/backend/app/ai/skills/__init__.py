"""Universal Skills Marketplace & SDK package.

Exposes configuration, models, interfaces, exceptions, BaseSkill SDK, decorators, permission manager,
voice registry, skill loader, skill registry, marketplace, skill memory, recommendation engine,
observability, and central UniversalSkillEngine.
"""

import sys
from typing import Any
from app.ai.skills.utils import lazy_import

__all__ = [
    "SkillConfiguration",
    "SkillStatus",
    "SkillCategory",
    "PermissionType",
    "VoiceCommandPhrase",
    "SkillManifest",
    "SkillMetadata",
    "SkillContext",
    "SkillRequest",
    "SkillResponse",
    "SkillTelemetry",
    "SkillHealth",
    "SkillMetrics",
    "ISkillEngine",
    "ISkillRegistry",
    "IMarketplace",
    "IVoiceRegistry",
    "ISkillLoader",
    "IPermissionManager",
    "ISkillMemory",
    "ISkillManager",
    "SkillEngineError",
    "SkillNotFoundError",
    "PermissionDeniedError",
    "SkillInstallationFailedError",
    "InvalidManifestError",
    "BaseSkill",
    "skill_decorator",
    "voice_command",
    "permission_required",
    "PermissionManager",
    "VoiceRegistry",
    "SkillLoader",
    "SkillRegistry",
    "Marketplace",
    "SkillMemory",
    "SkillRecommendationEngine",
    "SkillMetricsTracker",
    "SkillHealthMonitor",
    "SkillCache",
    "MockSkillProvider",
    "SkillManager",
    "UniversalSkillEngine",
]


def __getattr__(name: str) -> Any:
    return lazy_import(name)
