"""SDKConfiguration managing configurations and merging strategies.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from app.agent_sdk.exceptions import SDKConfigurationError


class SDKConfiguration(BaseModel):
    """Configuration schema for agent SDK instances."""

    settings: Dict[str, Any] = Field(default_factory=dict, description="Custom agent settings.")
    api_key: Optional[str] = Field(None, description="Optional API credentials key.")
    timeout: float = Field(30.0, description="Execution timeout limit in seconds.")

    def load(self, config_dict: Dict[str, Any]) -> None:
        """Loads configuration from a dictionary.

        Args:
            config_dict: Dictionary config values.

        Raises:
            SDKConfigurationError: If loading fails validation.
        """
        try:
            validated = SDKConfiguration(**config_dict)
            self.settings = validated.settings
            self.api_key = validated.api_key
            self.timeout = validated.timeout
        except Exception as e:
            raise SDKConfigurationError(f"Failed to load SDK configuration: {str(e)}") from e

    def validate(self) -> bool:
        """Validates configuration settings.

        Returns:
            True if config is valid; raises exception otherwise.

        Raises:
            SDKConfigurationError: If validation checks fail.
        """
        if self.timeout <= 0:
            raise SDKConfigurationError("Timeout must be a positive number.")
        return True

    def merge(self, other: "SDKConfiguration") -> "SDKConfiguration":
        """Merges another configuration into this one, returning a new instance.

        Args:
            other: Other configuration instance.

        Returns:
            Merged SDKConfiguration.
        """
        merged_settings = {**self.settings, **other.settings}
        merged_key = other.api_key if other.api_key is not None else self.api_key
        merged_timeout = other.timeout if other.timeout != 30.0 else self.timeout
        return SDKConfiguration(
            settings=merged_settings,
            api_key=merged_key,
            timeout=merged_timeout,
        )
