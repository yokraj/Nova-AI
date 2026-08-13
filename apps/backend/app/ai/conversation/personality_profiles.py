"""Personality Profiles Catalog defining tone, verbosity, and technical depth per profile.
"""

from typing import Dict, List, Optional
from app.ai.conversation.models import PersonalityMetadata, PersonalityProfileType


class PersonalityProfilesCatalog:
    """Catalog of conversational personalities for Nova AI OS."""

    def __init__(self) -> None:
        self._profiles: Dict[str, PersonalityMetadata] = self._seed_catalog()

    def _seed_catalog(self) -> Dict[str, PersonalityMetadata]:
        profiles = [
            PersonalityMetadata(
                profile_type=PersonalityProfileType.DEVELOPER,
                name="Developer Partner",
                tone="technical, code-focused, concise, and precise",
                verbosity="medium",
                technical_depth="high",
                voice_id="piper_en_developer",
            ),
            PersonalityMetadata(
                profile_type=PersonalityProfileType.TEACHER,
                name="Patient Educator",
                tone="instructive, encouraging, structured, and explanatory",
                verbosity="detailed",
                technical_depth="medium",
                voice_id="piper_en_teacher",
            ),
            PersonalityMetadata(
                profile_type=PersonalityProfileType.EXECUTIVE,
                name="Executive Advisor",
                tone="strategic, high-level, action-oriented, and crisp",
                verbosity="minimal",
                technical_depth="low",
                voice_id="piper_en_executive",
            ),
            PersonalityMetadata(
                profile_type=PersonalityProfileType.FRIENDLY,
                name="Friendly Companion",
                tone="warm, conversational, casual, and supportive",
                verbosity="medium",
                technical_depth="medium",
                voice_id="piper_en_friendly",
            ),
            PersonalityMetadata(
                profile_type=PersonalityProfileType.RESEARCHER,
                name="Academic Researcher",
                tone="rigorous, evidence-based, analytical, and objective",
                verbosity="detailed",
                technical_depth="high",
                voice_id="piper_en_researcher",
            ),
        ]
        return {p.profile_type.value: p for p in profiles}

    def get_profile(self, profile_type: PersonalityProfileType) -> PersonalityMetadata:
        """Retrieves profile metadata by PersonalityProfileType enum."""
        key = profile_type.value if hasattr(profile_type, "value") else str(profile_type)
        return self._profiles.get(key, self._profiles["developer"])

    def list_profiles(self) -> List[PersonalityMetadata]:
        """Lists all registered personality profiles."""
        return list(self._profiles.values())
