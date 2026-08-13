"""Configuration settings for the Autonomous Internet & Service Automation Platform."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceConfiguration(BaseSettings):
    """Central configuration for service domain workflows, OTPs, and payment safety."""

    model_config = SettingsConfigDict(
        env_prefix="NOVA_SERVICE_",
        case_sensitive=False,
        extra="ignore",
    )

    enabled: bool = Field(
        default=True,
        description="Whether service automation platform is active.",
    )
    auto_detect_websites: bool = Field(
        default=True,
        description="Whether to automatically detect site domains from requests.",
    )
    otp_timeout_seconds: float = Field(
        default=120.0,
        description="Timeout for user OTP code entry.",
    )
    payment_guard_strict: bool = Field(
        default=True,
        description="Enforce mandatory human approval for financial transactions.",
    )
    max_workflow_retries: int = Field(
        default=3,
        description="Maximum retry attempts per workflow step.",
    )
    default_currency: str = Field(
        default="INR",
        description="Default currency code.",
    )
