"""Skill Registry mapping voice intents and high-level user goals to plugin capabilities."""

from typing import Dict, List, Optional, Tuple
import structlog

from app.ai.plugins.models import PluginCapability

logger = structlog.get_logger("skill_registry")


class SkillRegistry:
    """Registry indexing voice intents and skill mappings."""

    def __init__(self) -> None:
        # intent_phrase_lower -> (plugin_id, capability_name)
        self._intent_map: Dict[str, Tuple[str, str]] = {}

    def register_skills(self, plugin_id: str, capability: PluginCapability) -> None:
        """Register voice intent phrases declared by a capability."""
        for intent in capability.voice_intents:
            phrase = intent.strip().lower()
            if phrase:
                self._intent_map[phrase] = (plugin_id, capability.name)
                logger.debug("Registered voice skill intent", intent=phrase, capability=capability.name)

    def unregister_plugin_skills(self, plugin_id: str) -> None:
        """Unregister all skills originating from a plugin."""
        to_remove = [k for k, (pid, _) in self._intent_map.items() if pid == plugin_id]
        for key in to_remove:
            self._intent_map.pop(key, None)

    def resolve_intent(self, user_utterance: str) -> Optional[Tuple[str, str]]:
        """Resolve a natural language voice command to (plugin_id, capability_name)."""
        text = user_utterance.strip().lower()

        # Direct match
        if text in self._intent_map:
            return self._intent_map[text]

        # Fuzzy substring match
        for intent_phrase, target in self._intent_map.items():
            if intent_phrase in text or text in intent_phrase:
                return target

        return None

    def list_skills() -> List[Dict[str, str]]:
        """Return all mapped voice skills."""
        return [
            {"intent": intent, "plugin_id": pid, "capability": cap}
            for intent, (pid, cap) in self._intent_map.items()
        ]

    def clear(self) -> None:
        """Clear all skill mappings."""
        self._intent_map.clear()
