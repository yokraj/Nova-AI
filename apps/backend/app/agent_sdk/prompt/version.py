"""VersionManager managing prompt version histories and rollbacks.
"""

from typing import Dict, List

from app.agent_sdk.prompt.exceptions import PromptValidationError
from app.agent_sdk.prompt.prompt import Prompt


class VersionManager:
    """Manages version histories and rollbacks for prompt templates."""

    def __init__(self) -> None:
        """Initializes VersionManager."""
        self._history: Dict[str, List[Prompt]] = {}

    def add_version(self, prompt: Prompt) -> None:
        """Appends a new version of a prompt to history tracker.

        Args:
            prompt: Prompt definition.
        """
        name = prompt.name
        if name not in self._history:
            self._history[name] = []
        self._history[name].append(prompt)

    def rollback(self, name: str, version: str) -> Prompt:
        """Rollbacks prompt configuration to a previous version.

        Args:
            name: Prompt template name.
            version: Target version key (e.g. 'v1').

        Returns:
            The Prompt instance matching version.

        Raises:
            PromptValidationError: If prompt name or version is not tracked.
        """
        history = self._history.get(name)
        if not history:
            raise PromptValidationError(f"No version history found for prompt '{name}'.")
        for p in history:
            if p.version == version:
                return p
        raise PromptValidationError(f"Version '{version}' for prompt '{name}' not found.")

    def history(self, name: str) -> List[Prompt]:
        """Lists historical versions of a prompt.

        Args:
            name: Prompt template name.

        Returns:
            List of Prompt versions.
        """
        return list(self._history.get(name, []))
