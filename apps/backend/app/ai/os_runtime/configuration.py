"""Configuration settings schema for AI Operating System Core, Always-On Voice Runtime & Continuous Cognitive Engine.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class OSRuntimeConfiguration(BaseModel):
    """System-wide configuration settings for Nova AI OS Background Runtime."""

    os_name: str = Field("Nova AI Operating System", description="Human-readable OS name")
    version: str = Field("3.4.19", description="OS Runtime version")
    environment: str = Field("production", description="Execution environment")
    enabled: bool = Field(True, description="Enable OS background service execution")
    auto_start_with_windows: bool = Field(True, description="Automatically start background service with Windows")
    system_tray_enabled: bool = Field(True, description="Enable Windows System Tray icon daemon")

    # Wake-Word & Voice Settings
    wake_word: str = Field("Hey Nova", description="Primary wake-word phrase")
    alternate_wake_words: List[str] = Field(default_factory=lambda: ["Nova", "Hey Assistant", "Computer"])
    wake_word_confidence_threshold: float = Field(0.85, description="Confidence threshold for wake-word activation")
    false_activation_suppression: bool = Field(True, description="Filter background conversation false positives")

    # VAD & Audio Settings
    vad_sensitivity: float = Field(0.75, description="Voice Activity Detection sensitivity")
    silence_timeout_ms: int = Field(800, description="Silence duration in ms signaling end of speech")
    noise_suppression_enabled: bool = Field(True, description="Enable background noise filtering")
    echo_cancellation_enabled: bool = Field(True, description="Enable acoustic echo cancellation")

    # Speech Recognition & Voice Auth
    stt_model: str = Field("whisper-large-v3", description="Speech-to-text recognition model")
    voice_auth_enabled: bool = Field(True, description="Enable owner voice print authentication")
    owner_voice_id: str = Field("owner_primary", description="Registered owner voice profile ID")

    # Early Reasoning & Interruption
    early_reasoning_enabled: bool = Field(True, description="Initiate speculative reasoning on partial transcription")
    speech_barge_in_enabled: bool = Field(True, description="Immediately stop TTS when user speaks")

    # Confirmations & Proactive Notifications
    confirmation_required_actions: List[str] = Field(
        default_factory=lambda: ["delete_file", "edit_registry", "admin_elevation", "make_payment", "shutdown_system"]
    )
    proactive_voice_notifications: bool = Field(True, description="Speak proactive system alerts")

    # Performance & Resources
    cache_ttl_seconds: int = Field(3600, description="Response cache TTL seconds")
    idle_cpu_threshold_percent: float = Field(5.0, description="Target idle CPU usage limit")
    idle_vram_release_delay_seconds: int = Field(300, description="Inactivity delay before freeing VRAM")
    heartbeat_interval_seconds: float = Field(5.0, description="Runtime watchdog heartbeat interval")
    mission_checkpoint_interval_seconds: float = Field(300.0, description="Background mission checkpointing interval")
