"""Unit tests for Voice Command Router.
"""

import os
import subprocess
import pytest
from app.ai.voice.voice_command_router import VoiceCommandRouter
from app.ai.voice.models import VoiceResponse


@pytest.fixture
def spoken_audio_bytes(tmp_path):
    """Generates real spoken WAV audio bytes using Windows SAPI voice synthesis."""
    wav_path = str(tmp_path / "router_spoken_sample.wav")
    ps_cmd = (
        f"$s = New-Object -ComObject SAPI.SpVoice; "
        f"$f = New-Object -ComObject SAPI.SpFileStream; "
        f"$f.Open('{wav_path}', 3, $false); "
        f"$s.AudioOutputStream = $f; "
        f"$s.Speak('Create cube in Blender'); "
        f"$f.Close()"
    )
    subprocess.run(["powershell", "-Command", ps_cmd], check=True, capture_output=True)
    with open(wav_path, "rb") as f:
        return f.read()


@pytest.mark.anyio
async def test_voice_command_router_end_to_end(tmp_path, spoken_audio_bytes):
    """Verifies end-to-end voice command routing from audio bytes to TTS audio response."""
    router = VoiceCommandRouter()
    router.tts_engine.storage_path = str(tmp_path / "voice_cache")
    
    res = await router.route_audio(spoken_audio_bytes, target_app="Blender")
    assert isinstance(res, VoiceResponse)
    assert res.audio_path is not None
    assert os.path.exists(res.audio_path)
    assert "Executed voice command" in res.text or "Voice command" in res.text


@pytest.mark.anyio
async def test_canonical_command_routing():
    """Verifies transcript routing uses the canonical Copilot pipeline."""
    router = VoiceCommandRouter()
    res = await router.route_transcript("Create sphere in Blender", target_app="Blender")
    assert isinstance(res, VoiceResponse)
    assert "Executed voice command" in res.text


@pytest.mark.anyio
async def test_voice_router_unsupported_app():
    """Verifies router handles unsupported commands gracefully."""
    router = VoiceCommandRouter()
    res = await router.route_transcript("Unknown Command", target_app="UnknownApp")
    assert isinstance(res, VoiceResponse)
