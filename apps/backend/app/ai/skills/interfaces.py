"""Abstract base interfaces and contracts for Universal Skills Marketplace & SDK.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.ai.skills.models import (
    PermissionType,
    SkillHealth,
    SkillManifest,
    SkillMetadata,
    SkillMetrics,
    SkillRequest,
    SkillResponse,
    VoiceCommandPhrase,
)


class ISkillRegistry(ABC):
    """Skill Registry contract managing registration, installation, and enabling."""

    @abstractmethod
    def register_skill(self, manifest: SkillManifest) -> None:
        """Registers skill manifest in registry."""
        pass

    @abstractmethod
    def get_skill(self, skill_id: str) -> Optional[SkillMetadata]:
        """Retrieves skill metadata by ID."""
        pass

    @abstractmethod
    def list_skills(self) -> List[SkillMetadata]:
        """Lists all registered skill metadata."""
        pass


class IMarketplace(ABC):
    """Marketplace contract managing search, installation, and version updates."""

    @abstractmethod
    async def search_skills(self, query: str, category: Optional[str] = None) -> List[SkillMetadata]:
        """Searches marketplace catalog for matching skills."""
        pass

    @abstractmethod
    async def install_skill(self, skill_id: str) -> bool:
        """Installs target skill package."""
        pass

    @abstractmethod
    async def uninstall_skill(self, skill_id: str) -> bool:
        """Uninstalls target skill package."""
        pass


class IVoiceRegistry(ABC):
    """Voice Registry contract registering voice command phrases dynamically for AI OS Kernel."""

    @abstractmethod
    def register_phrases(self, skill_id: str, phrases: List[VoiceCommandPhrase]) -> None:
        """Registers voice phrases for dynamic intent routing."""
        pass

    @abstractmethod
    def list_voice_commands(self) -> List[Dict[str, Any]]:
        """Lists all registered voice commands and phrases."""
        pass


class ISkillLoader(ABC):
    """Skill Loader contract handling dynamic loading and hot reloading."""

    @abstractmethod
    async def load_skill(self, skill_id: str) -> Any:
        """Loads skill instance dynamically."""
        pass


class IPermissionManager(ABC):
    """Permission Manager contract verifying security permission scopes."""

    @abstractmethod
    def check_permissions(self, required: List[PermissionType], granted: List[PermissionType]) -> bool:
        """Verifies if required permissions are granted."""
        pass


class ISkillMemory(ABC):
    """Skill Memory contract tracking usage statistics and optimization preferences."""

    @abstractmethod
    def record_usage(self, skill_id: str, success: bool, latency_ms: float) -> None:
        """Records skill execution telemetry."""
        pass


class ISkillManager(ABC):
    """Skill Manager administrative contract."""

    @abstractmethod
    async def start(self) -> None:
        """Starts skill platform manager."""
        pass


class ISkillEngine(ABC):
    """Central Universal Skill Engine facade contract."""

    @abstractmethod
    async def install_skill(self, skill_id: str) -> bool:
        """Installs skill from marketplace."""
        pass

    @abstractmethod
    async def uninstall_skill(self, skill_id: str) -> bool:
        """Uninstalls skill from local registry."""
        pass

    @abstractmethod
    async def enable_skill(self, skill_id: str) -> bool:
        """Enables target skill."""
        pass

    @abstractmethod
    async def disable_skill(self, skill_id: str) -> bool:
        """Disables target skill."""
        pass

    @abstractmethod
    async def search_skills(self, query: str, category: Optional[str] = None) -> List[SkillMetadata]:
        """Searches skills marketplace."""
        pass

    @abstractmethod
    async def list_skills(self) -> List[SkillMetadata]:
        """Lists installed skills."""
        pass

    @abstractmethod
    async def skill_info(self, skill_id: str) -> Optional[SkillMetadata]:
        """Retrieves skill metadata."""
        pass

    @abstractmethod
    async def voice_commands(self) -> List[Dict[str, Any]]:
        """Lists all registered voice commands."""
        pass

    @abstractmethod
    async def execute_skill(self, skill_id: str, action: str = "execute", **kwargs: Any) -> SkillResponse:
        """Executes a skill action."""
        pass
