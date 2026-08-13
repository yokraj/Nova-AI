"""Configuration for the Universal Plugin & Skill Integration Platform."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PluginConfiguration(BaseSettings):
    """Central configuration for discovery, loading, permissions, and sandboxing."""

    model_config = SettingsConfigDict(
        env_prefix="NOVA_PLUGIN_",
        case_sensitive=False,
        extra="ignore",
    )

    plugins_dir: str = Field(
        default="./plugins",
        description="Root directory where local plugins are stored and scanned.",
    )
    auto_discover: bool = Field(
        default=True,
        description="Whether to scan plugins_dir automatically at startup.",
    )
    enable_sandbox: bool = Field(
        default=True,
        description="Whether to run plugin capabilities inside isolation sandbox.",
    )
    sandbox_timeout_seconds: float = Field(
        default=30.0,
        description="Maximum execution duration before sandbox terminates execution.",
    )
    verify_signatures: bool = Field(
        default=False,
        description="Enforce signature validation for installed plugin packages.",
    )
    max_installed_plugins: int = Field(
        default=100,
        description="Maximum number of active registered plugins.",
    )
    cache_ttl_seconds: int = Field(
        default=300,
        description="TTL for cached capability discovery and execution results.",
    )
