"""Configuration settings for Ambient Intelligence & Continuous Voice Assistant."""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AmbientConfiguration(BaseSettings):
    """Central configuration for microphone listening, wake words, desktop monitors, and privacy mode."""

    model_config = SettingsConfigDict(
        env_prefix="NOVA_AMBIENT_",
        case_sensitive=False,
        extra="ignore",
    )

    enabled: bool = Field(
        default=True,
        description="Whether ambient intelligence engine is active.",
    )
    microphone_enabled: bool = Field(
        default=True,
        description="Whether continuous microphone listening is active.",
    )
    privacy_mode: bool = Field(
        default=False,
        description="Privacy mode: disables microphone and screen/clipboard monitoring.",
    )
    incognito_mode: bool = Field(
        default=False,
        description="Incognito mode: disables conversation logging.",
    )
    wake_words: List[str] = Field(
        default_factory=lambda: ["Hey Nova", "Nova"],
        description="Supported wake word phrases.",
    )
    wake_word_cooldown_seconds: float = Field(
        default=2.0,
        description="Cooldown duration after wake word detection to avoid duplicate triggers.",
    )
    vad_sensitivity: float = Field(
        default=0.6,
        description="Voice Activity Detection (VAD) threshold (0.0 to 1.0).",
    )
    desktop_monitor_interval_seconds: float = Field(
        default=3.0,
        description="Interval for polling active window and clipboard state.",
    )
    idle_threshold_seconds: float = Field(
        default=300.0,
        description="Inactivity duration to trigger idle state (seconds).",
    )
