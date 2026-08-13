"""Personality Engine managing active personality profile assignment and voice tuning.
"""

from typing import Dict
from app.ai.conversation.interfaces import IPersonalityEngine
from app.ai.conversation.models import PersonalityMetadata, PersonalityProfileType
from app.ai.conversation.personality_profiles import PersonalityProfilesCatalog


class PersonalityEngine(IPersonalityEngine):
    """Manages active personality assignment across conversation sessions."""

    def __init__(self) -> None:
        self.catalog = PersonalityProfilesCatalog()
        self._session_profiles: Dict[str, PersonalityMetadata] = {}

    def get_profile(self, profile_type: PersonalityProfileType) -> PersonalityMetadata:
        """Retrieves profile metadata from catalog."""
        return self.catalog.get_profile(profile_type)

    def set_active_profile(self, session_id: str, profile_type: PersonalityProfileType) -> PersonalityMetadata:
        """Sets active personality profile for target session_id."""
        meta = self.catalog.get_profile(profile_type)
        self._session_profiles[session_id] = meta
        return meta

    def get_active_profile(self, session_id: str) -> PersonalityMetadata:
        """Retrieves active personality profile for session_id."""
        return self._session_profiles.get(session_id, self.catalog.get_profile(PersonalityProfileType.DEVELOPER))
