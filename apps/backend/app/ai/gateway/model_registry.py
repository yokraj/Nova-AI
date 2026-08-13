"""Model Registry maintaining metadata for all supported AI models.
"""

from typing import Dict, List, Optional
from app.ai.models import AIModelInfo, ProviderCapability


class ModelRegistry:
    """Registry maintaining metadata properties for all supported models."""

    def __init__(self) -> None:
        """Initializes ModelRegistry."""
        self._models: Dict[str, AIModelInfo] = {}
        self._default_model: Optional[str] = None

    def register_model(self, model: AIModelInfo, is_default: bool = False, bypass_default: bool = False) -> None:
        """Registers a new model capability configuration.

        Args:
            model: AIModelInfo details.
            is_default: If true, sets this model as default.
            bypass_default: If true, prevents setting as default if registry is empty.
        """
        self._models[model.name] = model
        if is_default or (not self._default_model and not bypass_default):
            self._default_model = model.name

    def model(self, name: str) -> Optional[AIModelInfo]:
        """Fetches metadata configuration for a model name.

        Args:
            name: The model identifier string.

        Returns:
            AIModelInfo instance, or None.
        """
        return self._models.get(name)

    def default_model(self) -> Optional[str]:
        """Returns the fallback default model name.

        Returns:
            Default model string identifier, or None.
        """
        return self._default_model

    def provider_models(self, capability: Optional[ProviderCapability] = None) -> List[str]:
        """Returns a list of model names, optionally filtered by capability.

        Args:
            capability: Optional capability tag to filter by.

        Returns:
            List of supported model names.
        """
        if not capability:
            return list(self._models.keys())
        return [
            name
            for name, meta in self._models.items()
            if capability in meta.capabilities
        ]
