"""User Memory Module.

Maintains persistent user preference profiles, writing styles, favorite programming languages,
frameworks, tools, and coding style habits.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.memory.repository import MemoryRepository

logger = structlog.get_logger(__name__)


class UserMemoryManager:
    """Enterprise User Preferences & Style Habit Memory Manager."""

    def __init__(self, repository: MemoryRepository) -> None:
        self.repository = repository
        logger.info("user_memory_manager_initialized")

    async def update_preferences(
        self,
        user_id: str,
        writing_style: Optional[str] = None,
        favorite_languages: Optional[List[str]] = None,
        favorite_frameworks: Optional[List[str]] = None,
        frequent_tools: Optional[List[str]] = None,
        coding_style: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Updates user preference memory entry."""
        pref_content = (
            f"User Profile [{user_id}]: Writing Style: {writing_style or 'Default'}. "
            f"Languages: {favorite_languages or []}. Frameworks: {favorite_frameworks or []}."
        )

        entry = await self.repository.create_entry(
            title=f"User Preferences: {user_id}",
            content=pref_content,
            summary=pref_content[:100],
            memory_type="user_preference",
            user_id=user_id,
            is_pinned=True,
            metadata_json={
                "writing_style": writing_style,
                "favorite_languages": favorite_languages or [],
                "favorite_frameworks": favorite_frameworks or [],
                "frequent_tools": frequent_tools or [],
                "coding_style": coding_style,
            },
        )
        logger.info("user_preferences_saved", user_id=user_id)
        return {"memory_id": entry.id, "user_id": user_id}

    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Retrieves active user preference profile memory."""
        entries = await self.repository.search_entries(user_id=user_id, memory_type="user_preference", limit=1)
        if entries:
            return entries[0].metadata_json or {}
        return {
            "writing_style": "Concise, technical, and structured",
            "favorite_languages": ["Python", "TypeScript"],
            "favorite_frameworks": ["FastAPI", "React"],
            "frequent_tools": ["python_interpreter", "git_repository"],
        }
