"""ModelHelper querying registered models and active capabilities.
"""

from typing import List, Optional

from app.ai.gateway.ai_gateway import AIGateway
from app.agent_sdk.ai.exceptions import ModelUnavailableError


class ModelHelper:
    """Helper for checking AI models, providers, and capabilities."""

    def __init__(self, gateway: AIGateway) -> None:
        """Initializes ModelHelper.

        Args:
            gateway: Active AIGateway instance.
        """
        self.gateway = gateway

    def list_models(self) -> List[str]:
        """Lists all registered models in the AI Gateway.

        Returns:
            List of supported model identifiers.
        """
        return self.gateway.model_registry.provider_models()

    def current_model(self) -> str:
        """Returns the default active model identifier.

        Returns:
            Default active model name.

        Raises:
            ModelUnavailableError: If no default model is found.
        """
        model = self.gateway.model_registry.default_model()
        if not model:
            models = self.list_models()
            if models:
                return models[0]
            raise ModelUnavailableError("No active default model is configured.")
        return model

    def current_provider(self) -> str:
        """Returns the active provider identifier.

        Returns:
            Active default provider name.
        """
        try:
            model = self.current_model()
            for provider_name in self.gateway.provider_registry.list():
                provider = self.gateway.provider_registry.provider(provider_name)
                if hasattr(provider, "supports_model") and provider.supports_model(model):
                    return provider_name
            providers = self.gateway.provider_registry.list()
            if providers:
                return providers[0]
        except Exception:
            pass
        return "ollama"

    def model_capabilities(self, model_name: str) -> List[str]:
        """Lists the capabilities supported by the specified model.

        Args:
            model_name: The name of the model.

        Returns:
            List of capability names.

        Raises:
            ModelUnavailableError: If specified model is not registered.
        """
        info = self.gateway.model_registry.model(model_name)
        if not info:
            raise ModelUnavailableError(f"Model '{model_name}' is not registered.")
        return [cap.value for cap in info.capabilities]
