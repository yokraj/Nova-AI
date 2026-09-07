"""Unit tests for Voice Activation Manager.
"""

import pytest
from app.ai.voice.voice_activation import VoiceActivationManager


def test_wake_word_detection():
    """Verifies wake word keyword triggers activation."""
    mgr = VoiceActivationManager(keyword="Nova")
    triggered = mgr.process_audio_chunk(b"Nova, start listening")
    assert triggered is True
    assert mgr.is_listening() is True


def test_voice_session_activation_lifecycle():
    """Verifies activation session start, active check, and deactivation."""
    mgr = VoiceActivationManager()
    session = mgr.activate_session()
    assert session.status == "active"
    assert mgr.is_listening() is True

    mgr.deactivate_session()
    assert mgr.is_listening() is False
    assert mgr.active_session is None


def test_voice_activation_non_trigger():
    """Verifies non-keyword audio chunks do not trigger activation."""
    mgr = VoiceActivationManager(keyword="Nova")
    triggered = mgr.process_audio_chunk(b"Hello system")
    assert triggered is False
    assert mgr.is_listening() is False


def test_voice_activation_empty_chunk():
    """Verifies empty audio chunks return False."""
    mgr = VoiceActivationManager()
    assert mgr.process_audio_chunk(b"") is False
