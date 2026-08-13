"""Caching layer for generated audio files and text transcriptions.
"""

import json
import os
from typing import Dict, Any, Optional

class VoiceCache:
    """Caches speech transcripts and generated voice wave path configurations."""

    def __init__(self, storage_path: str = ".nova/cache/voice/") -> None:
        self.storage_path = storage_path
        self.cache_file = os.path.join(storage_path, "voice_cache.json")
        self.data: Dict[str, Any] = {
            "transcripts": {},
            "audio_metadata": {}
        }
        self.load()

    def load(self) -> None:
        """Loads cached transcripts from file."""
        if not os.path.exists(self.cache_file):
            return
        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception:
            pass

    def save(self) -> None:
        """Saves current state to cache file."""
        try:
            os.makedirs(self.storage_path, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def get_transcript(self, audio_hash: str) -> Optional[str]:
        """Returns cached transcript if available."""
        return self.data["transcripts"].get(audio_hash)

    def cache_transcript(self, audio_hash: str, text: str) -> None:
        """Stores a transcript value."""
        self.data["transcripts"][audio_hash] = text
        self.save()
