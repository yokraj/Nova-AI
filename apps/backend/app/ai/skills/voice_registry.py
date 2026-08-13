"""Voice Command Registry dynamically registering spoken phrases and aliases for AI OS Kernel.
"""

from typing import Any, Dict, List
from app.ai.skills.interfaces import IVoiceRegistry
from app.ai.skills.models import VoiceCommandPhrase


class VoiceRegistry(IVoiceRegistry):
    """Dynamic voice phrase registry allowing AI OS Kernel to discover installed skill commands."""

    def __init__(self) -> None:
        self._phrases: Dict[str, List[VoiceCommandPhrase]] = {}

    def register_phrases(self, skill_id: str, phrases: List[VoiceCommandPhrase]) -> None:
        """Registers voice phrases for target skill_id.

        Args:
            skill_id: Target skill ID string.
            phrases: List of VoiceCommandPhrase instances.
        """
        self._phrases[skill_id] = phrases

    def list_voice_commands(self) -> List[Dict[str, Any]]:
        """Lists all registered voice commands across all skills for Kernel intent routing."""
        commands = []
        for skill_id, phrase_list in self._phrases.items():
            for p in phrase_list:
                commands.append({
                    "skill_id": skill_id,
                    "phrase": p.phrase,
                    "aliases": p.aliases,
                    "examples": p.examples,
                })
        return commands
