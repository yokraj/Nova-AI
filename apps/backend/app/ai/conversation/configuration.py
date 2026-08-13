"""Configuration settings and schemas for Human-Like Conversation & EI Engine.
"""

from typing import Any, Dict
from pydantic import BaseModel, Field


class ConversationConfiguration(BaseModel):
    """Configuration schema for Human-Like Conversation and Emotional Intelligence subsystem."""

    default_personality: str = Field("DEVELOPER", description="Default active personality profile name")
    emotion_detection_enabled: bool = Field(True, description="Enable real-time emotion detection and speech adaptation")
    streaming_chunk_size: int = Field(16, description="Token chunk size for streaming conversation responses")
    max_history_turns: int = Field(50, description="Maximum turn history retained before compression")
    compression_threshold_tokens: int = Field(4096, description="Token limit triggering history summarization")
    auto_followup_enabled: bool = Field(True, description="Automatically resolve implicit follow-up references")
    clarification_options_count: int = Field(3, description="Number of choices presented during clarification")
    cache_ttl_seconds: int = Field(3600, description="Cache TTL for conversation context snapshots")
    extra_settings: Dict[str, Any] = Field(default_factory=dict, description="Additional custom settings")
