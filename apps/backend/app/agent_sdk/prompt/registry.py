"""PromptRegistry cataloging active templates and versions.
"""

from typing import Dict, List, Optional

from app.agent_sdk.prompt.prompt import Prompt
from app.agent_sdk.prompt.version import VersionManager


class PromptRegistry:
    """Central registry maintaining and indexing active prompt definitions."""

    def __init__(self) -> None:
        """Initializes PromptRegistry."""
        self._prompts: Dict[str, Prompt] = {}
        self.version_manager = VersionManager()

    def register(self, prompt: Prompt) -> None:
        """Registers a new prompt template.

        Args:
            prompt: Prompt definition.
        """
        self._prompts[prompt.name] = prompt
        self.version_manager.add_version(prompt)

    def unregister(self, name: str) -> None:
        """Removes a prompt template registration.

        Args:
            name: Prompt name.
        """
        self._prompts.pop(name, None)

    def find(self, name: str) -> Optional[Prompt]:
        """Resolves a prompt definition by name.

        Args:
            name: Prompt template name.

        Returns:
            Prompt instance, or None.
        """
        return self._prompts.get(name)

    def find_by_category(self, category: str) -> List[Prompt]:
        """Resolves prompts matching a category.

        Args:
            category: Target category path.

        Returns:
            List of matching Prompts.
        """
        return [p for p in self._prompts.values() if p.category == category]

    def find_by_tag(self, tag: str) -> List[Prompt]:
        """Resolves prompts matching a tag.

        Args:
            tag: Target tag string.

        Returns:
            List of matching Prompts.
        """
        return [p for p in self._prompts.values() if tag in p.tags]

    def latest_version(self, name: str) -> Optional[Prompt]:
        """Resolves the latest version of a prompt name.

        Args:
            name: Prompt template name.

        Returns:
            Latest Prompt version instance, or None.
        """
        versions = self.version_manager.history(name)
        if not versions:
            return None
        return versions[-1]
