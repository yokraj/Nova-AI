"""Skill SDK Decorators for registering capabilities, voice commands, and permission requirements.
"""

import functools
from typing import Any, Callable, List
from app.ai.skills.models import PermissionType, VoiceCommandPhrase


def skill_decorator(skill_id: str, name: str, category: str = "custom") -> Callable:
    """Decorator marking class as a Nova Skill."""

    def decorator(cls: Any) -> Any:
        cls._is_nova_skill = True
        cls._skill_id = skill_id
        cls._skill_name = name
        cls._skill_category = category
        return cls

    return decorator


def voice_command(phrase: str, aliases: List[str] = None) -> Callable:
    """Decorator registering voice phrase for dynamic Kernel intent routing."""

    def decorator(func: Callable) -> Callable:
        func._voice_phrase = phrase
        func._voice_aliases = aliases or []
        return func

    return decorator


def permission_required(permission: PermissionType) -> Callable:
    """Decorator declaring security permission requirements."""

    def decorator(func: Callable) -> Callable:
        if not hasattr(func, "_required_permissions"):
            func._required_permissions = []
        func._required_permissions.append(permission)
        return func

    return decorator
