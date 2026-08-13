"""Configuration schema for the Enterprise Voice Intelligence Layer.
"""

from pydantic import BaseModel, Field

class VoiceConfiguration(BaseModel):
    """Configuration options for voice assistants, speech-to-text, and TTS engines."""

    enabled: bool = Field(True, description="Enables voice assistant features.")
    provider: str = Field("whisper", description="Speech recognition provider name.")
    language: str = Field("en", description="Default translation and speech language tag.")
    sample_rate: int = Field(16000, description="Target audio sampling rate in Hz.")
    wake_word_enabled: bool = Field(True, description="Enables continuous wake word detection.")
    wake_word: str = Field("Nova", description="Target wake keyword trigger string.")
    offline_mode: bool = Field(True, description="Enforce zero-cost offline local modes execution.")
    max_session_time: int = Field(300, description="Max session connection timeout duration in seconds.")
