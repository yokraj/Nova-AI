"""Unit tests for Local STT Engine with isolated neural Whisper.
"""

import os
import subprocess
import pytest
from app.ai.voice.stt_engine import LocalSTTEngine
from app.ai.voice.exceptions import SpeechRecognitionError


@pytest.fixture
def spoken_wav_sample(tmp_path):
    """Generates a real spoken WAV audio sample using native Windows TTS for neural STT testing."""
    wav_path = str(tmp_path / "test_spoken_sample.wav")
    ps_cmd = (
        f"$s = New-Object -ComObject SAPI.SpVoice; "
        f"$f = New-Object -ComObject SAPI.SpFileStream; "
        f"$f.Open('{wav_path}', 3, $false); "
        f"$s.AudioOutputStream = $f; "
        f"$s.Speak('Create cube in Blender'); "
        f"$f.Close()"
    )
    subprocess.run(["powershell", "-Command", ps_cmd], check=True, capture_output=True)
    return wav_path


@pytest.mark.anyio
async def test_local_stt_availability():
    """Verifies local STT availability and offline status."""
    stt = LocalSTTEngine()
    assert stt.is_available() is True
    assert stt.is_offline is True


@pytest.mark.anyio
async def test_local_stt_real_transcription(spoken_wav_sample):
    """Verifies REAL neural offline transcription of a spoken WAV audio sample using isolated Whisper."""
    stt = LocalSTTEngine()
    with open(spoken_wav_sample, "rb") as f:
        audio_bytes = f.read()

    result = await stt.transcribe(audio_bytes)
    assert result.transcript is not None
    assert len(result.transcript) > 0
    assert "cube" in result.transcript.lower() or "blender" in result.transcript.lower() or "create" in result.transcript.lower()
    assert result.confidence > 0.5


@pytest.mark.anyio
async def test_stt_failure_on_empty_audio():
    """Verifies SpeechRecognitionError is raised on empty audio input."""
    stt = LocalSTTEngine()
    with pytest.raises(SpeechRecognitionError):
        await stt.transcribe(b"")


@pytest.mark.anyio
async def test_stt_failure_on_corrupted_audio():
    """Verifies SpeechRecognitionError is raised on corrupted audio input."""
    stt = LocalSTTEngine()
    with pytest.raises(SpeechRecognitionError):
        await stt.transcribe(b"corrupted_bytes_data")


@pytest.mark.anyio
async def test_no_cloud_stt_guarantee():
    """Verifies cloud API configuration is explicitly rejected."""
    with pytest.raises(ValueError, match="Cloud STT providers are strictly forbidden"):
        LocalSTTEngine(allow_cloud=True)
