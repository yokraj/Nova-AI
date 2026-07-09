"""Model metadata configuration and Provider registries for Nova AI.

Stores token configurations, costs per 1K tokens, capabilities,
and handles registration lookup loops.
"""

from typing import Dict, List, Optional

from app.ai.provider import BaseProvider


class ModelMetadata:
    """Metadata configurations for an AI model."""

    def __init__(
        self,
        name: str,
        context_window: int,
        max_output_tokens: int,
        capabilities: List[str],
        input_cost_per_1k: float,
        output_cost_per_1k: float,
    ) -> None:
        """Initializes the ModelMetadata details.

        Args:
            name: Model name identifier.
            context_window: The maximum input context tokens window length.
            max_output_tokens: Maximum output tokens size.
            capabilities: List of capability tags (e.g. "text", "vision").
            input_cost_per_1k: Cost in USD per 1K input tokens.
            output_cost_per_1k: Cost in USD per 1K output tokens.
        """
        self.name = name
        self.context_window = context_window
        self.max_output_tokens = max_output_tokens
        self.capabilities = capabilities
        self.input_cost_per_1k = input_cost_per_1k
        self.output_cost_per_1k = output_cost_per_1k


class ModelRegistry:
    """Registry maintaining configurations metadata for supported models."""

    def __init__(self) -> None:
        self._models: Dict[str, ModelMetadata] = {}
        # Pre-register common baseline models
        self.register(
            ModelMetadata(
                "gpt-4o", 128000, 4096, ["text", "vision"], 0.005, 0.015
            )
        )
        self.register(
            ModelMetadata(
                "claude-3-opus", 200000, 4096, ["text", "vision"], 0.015, 0.075
            )
        )
        self.register(
            ModelMetadata("llama-3-70b", 8192, 2048, ["text"], 0.0007, 0.0009)
        )

    def register(self, metadata: ModelMetadata) -> None:
        """Registers a new model configuration mapping."""
        self._models[metadata.name] = metadata

    def get(self, name: str) -> Optional[ModelMetadata]:
        """Fetches metadata configuration for a model.

        Args:
            name: The model identifier string.

        Returns:
            ModelMetadata instance, or None if not registered.
        """
        return self._models.get(name)


class ProviderRegistry:
    """Registry maintaining active provider adapters instances."""

    def __init__(self) -> None:
        self._providers: Dict[str, BaseProvider] = {}

    def register(self, provider: BaseProvider) -> None:
        """Registers an AI provider implementation class instance.

        Args:
            provider: The BaseProvider subclass instance.
        """
        self._providers[provider.get_name()] = provider

    def get(self, name: str) -> Optional[BaseProvider]:
        """Fetches a registered provider instance by name.

        Args:
            name: The provider name string.

        Returns:
            The BaseProvider instance, or None.
        """
        return self._providers.get(name)

    def select_for_model(self, model: str) -> Optional[BaseProvider]:
        """Discovers the first registered provider supporting the model.

        Args:
            model: The target model name.

        Returns:
            The matched BaseProvider instance, or None.
        """
        for provider in self._providers.values():
            if provider.supports_model(model):
                return provider
        return None
