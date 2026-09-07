"""Unit tests for Local TTS Engine.
"""

import os
import pytest
from app.ai.voice.tts_engine import LocalTTSEngine
from app.ai.voice.exceptions import TextToSpeechError


@pytest.mark.anyio
async def test_local_tts_availability():
    """Verifies local TTS availability."""
    tts = LocalTTSEngine()
    assert tts.is_available() is True
    assert tts.is_offline is True


@pytest.mark.anyio
async def test_local_tts_real_synthesis(tmp_path):
    """Verifies synthesis produces a valid, non-empty WAV file."""
    storage_dir = str(tmp_path / "voice_cache")
    tts = LocalTTSEngine(storage_path=storage_dir)
    wav_path = await tts.synthesize("State verified successfully.")
    assert os.path.exists(wav_path)
    assert os.path.getsize(wav_path) > 0
    assert wav_path.endswith(".wav")


@pytest.mark.anyio
async def test_tts_failure_on_empty_text():
    """Verifies TextToSpeechError is raised on empty or whitespace text."""
    tts = LocalTTSEngine()
    with pytest.raises(TextToSpeechError):
        await tts.synthesize("")

    with pytest.raises(TextToSpeechError):
        await tts.synthesize("   ")


@pytest.mark.anyio
async def test_no_cloud_tts_guarantee():
    """Verifies cloud TTS configuration is explicitly rejected."""
    with pytest.raises(ValueError, match="Cloud TTS providers are strictly forbidden"):
        LocalTTSEngine(allow_cloud=True)
