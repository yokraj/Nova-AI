"""Enterprise Voice Intelligence Layer – lazy package exports.

Symbols are loaded on first access via __getattr__ so that:

- Importing *any* submodule of app.ai.voice does NOT trigger the full
  engine initialisation chain (LocalVoiceEngine -> LocalMemoryEngine -> httpx).
- Unit / manual tests can import lightweight components in isolation.
- Start-up time and memory footprint are reduced.
- Plugin / feature-flag architectures can gate heavy imports at runtime.

Usage is identical to a normal package import:

    from app.ai.voice import LocalVoiceEngine, VoiceConfiguration
    from app.ai.voice import WakeWordDetector, VoiceIntentClassifier
"""

from __future__ import annotations

__all__ = [
    # Core engine
    "LocalVoiceEngine",
    # Configuration
    "VoiceConfiguration",
    # Exceptions
    "VoiceEngineError",
    "SpeechRecognitionError",
    "TextToSpeechError",
    "WakeWordError",
    "VoiceSessionError",
    # Domain models
    "VoiceRequest",
    "VoiceResponse",
    "SpeechResult",
    "VoiceSession",
    "VoiceCommand",
    # Interfaces / ABCs
    "ISpeechRecognizer",
    "ITextToSpeechProvider",
    "IWakeWordDetector",
    "IVoiceSessionManager",
    # Concrete providers
    "WhisperSpeechRecognizer",
    "MockSpeechRecognizer",
    "LocalTTSProvider",
    "MockTTSProvider",
    "WakeWordDetector",
    "VoiceSessionManager",
    # Pipeline helpers
    "VoiceIntentClassifier",
    "VoiceContextBuilder",
    # Observability
    "VoiceMetricsTracker",
    "VoiceHealthMonitor",
    # Utilities
    "VoiceCache",
    "calculate_audio_hash",
]

# ---------------------------------------------------------------------------
# Lazy import map  {exported_name: (module_path, attr_in_module)}
# ---------------------------------------------------------------------------
_LAZY: dict[str, tuple[str, str]] = {
    # Core engine – most expensive: pulls in LocalMemoryEngine / httpx
    "LocalVoiceEngine":         (".engine",                          "LocalVoiceEngine"),
    # Configuration – lightweight Pydantic model
    "VoiceConfiguration":       (".configuration",                   "VoiceConfiguration"),
    # Exceptions – no heavy deps
    "VoiceEngineError":         (".exceptions",                      "VoiceEngineError"),
    "SpeechRecognitionError":   (".exceptions",                      "SpeechRecognitionError"),
    "TextToSpeechError":        (".exceptions",                      "TextToSpeechError"),
    "WakeWordError":            (".exceptions",                      "WakeWordError"),
    "VoiceSessionError":        (".exceptions",                      "VoiceSessionError"),
    # Domain models
    "VoiceRequest":             (".models",                          "VoiceRequest"),
    "VoiceResponse":            (".models",                          "VoiceResponse"),
    "SpeechResult":             (".models",                          "SpeechResult"),
    "VoiceSession":             (".models",                          "VoiceSession"),
    "VoiceCommand":             (".models",                          "VoiceCommand"),
    # Interfaces
    "ISpeechRecognizer":        (".interfaces",                      "ISpeechRecognizer"),
    "ITextToSpeechProvider":    (".interfaces",                      "ITextToSpeechProvider"),
    "IWakeWordDetector":        (".interfaces",                      "IWakeWordDetector"),
    "IVoiceSessionManager":     (".interfaces",                      "IVoiceSessionManager"),
    # Concrete providers
    "WhisperSpeechRecognizer":  (".speech_recognition.whisper_provider", "WhisperSpeechRecognizer"),
    "MockSpeechRecognizer":     (".speech_recognition.whisper_provider", "MockSpeechRecognizer"),
    "LocalTTSProvider":         (".text_to_speech.tts_provider",     "LocalTTSProvider"),
    "MockTTSProvider":          (".text_to_speech.tts_provider",     "MockTTSProvider"),
    "WakeWordDetector":         (".wake_word.wake_word_detector",    "WakeWordDetector"),
    "VoiceSessionManager":      (".session.session_manager",         "VoiceSessionManager"),
    # Pipeline helpers
    "VoiceIntentClassifier":    (".intent_classifier",               "VoiceIntentClassifier"),
    "VoiceContextBuilder":      (".context_builder",                 "VoiceContextBuilder"),
    # Observability
    "VoiceMetricsTracker":      (".metrics",                         "VoiceMetricsTracker"),
    "VoiceHealthMonitor":       (".health",                          "VoiceHealthMonitor"),
    # Utilities
    "VoiceCache":               (".cache",                           "VoiceCache"),
    "calculate_audio_hash":     (".utils",                           "calculate_audio_hash"),
}


def __getattr__(name: str):  # noqa: ANN001, ANN201
    """Resolve voice package exports on first access (PEP 562)."""
    if name in _LAZY:
        module_path, attr = _LAZY[name]
        import importlib
        module = importlib.import_module(module_path, package=__name__)
        obj = getattr(module, attr)
        # Cache in this module's namespace so subsequent accesses are O(1)
        globals()[name] = obj
        return obj
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
