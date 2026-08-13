"""Tests for the Enterprise Voice Intelligence Layer.
"""

import pytest
from uuid import UUID
from app.ai.voice.configuration import VoiceConfiguration
from app.ai.voice.speech_recognition.whisper_provider import MockSpeechRecognizer
from app.ai.voice.text_to_speech.tts_provider import MockTTSProvider
from app.ai.voice.wake_word.wake_word_detector import WakeWordDetector
from app.ai.voice.session.session_manager import VoiceSessionManager
from app.ai.voice.intent_classifier import VoiceIntentClassifier
from app.ai.voice.models import VoiceRequest, SpeechResult
from app.ai.voice.engine import LocalVoiceEngine
from app.ai.gateway import AIGateway
from app.ai.gateway.model_registry import ModelRegistry
from app.ai.gateway.provider_registry import ProviderRegistry
from app.ai.gateway.provider_factory import ProviderFactory
from app.ai.gateway.retry_policy import RetryPolicy
from app.ai.gateway.timeout_policy import TimeoutPolicy
from app.ai.models import ChatResponse, PromptMessage, AIUsage, AIModelInfo, ModelType, ProviderCapability
from app.ai.providers.contracts import ILLMProvider

@pytest.mark.anyio
async def test_voice_configuration():
    """Verifies that the configuration validates parameters correctly."""
    config = VoiceConfiguration()
    assert config.wake_word == "Nova"
    assert config.offline_mode is True

@pytest.mark.anyio
async def test_mock_speech_recognition():
    """Verifies mock speech recognizer transcribes dummy audio bytes."""
    recognizer = MockSpeechRecognizer()
    result = await recognizer.transcribe(b"Nova, fix Python bug")
    assert result.transcript == "Nova, fix Python bug"
    assert result.confidence == 0.98

@pytest.mark.anyio
async def test_tts_generation():
    """Verifies text synthesis saves mock wav file."""
    tts = MockTTSProvider()
    file_path = await tts.synthesize("Hello world")
    assert file_path.endswith(".wav")

@pytest.mark.anyio
async def test_wake_word_detection():
    """Verifies wake word triggers on keyword 'Nova'."""
    detector = WakeWordDetector(keyword="Nova")
    assert detector.detect(b"Nova, start listening") is True
    assert detector.detect(b"Hello system") is False

@pytest.mark.anyio
async def test_intent_classification():
    """Verifies intent mapping rules."""
    classifier = VoiceIntentClassifier()
    cmd1 = classifier.classify_intent("fix python error in user login")
    assert cmd1.intent == "debugging"
    assert cmd1.command_type == "software_engineer"

    cmd2 = classifier.classify_intent("remember to commit the code tonight")
    assert cmd2.intent == "remember_this"
    assert cmd2.command_type == "memory"

@pytest.mark.anyio
async def test_session_creation():
    """Verifies session manager opens and closes sessions."""
    manager = VoiceSessionManager()
    session = manager.create_session()
    assert isinstance(session.id, UUID)
    assert session.status == "active"
    
    manager.close_session(session.id)
    assert session.status == "closed"

@pytest.mark.anyio
async def test_voice_pipeline_execution():
    """Verifies full Voice pipeline execution from audio bytes to audio response."""
    provider_registry = ProviderRegistry()
    model_registry = ModelRegistry()

    # Register default model
    model_registry.register_model(
        AIModelInfo(
            name="qwen2.5-coder",
            type=ModelType.TEXT,
            context_window=4096,
            max_output_tokens=1000,
            capabilities=[ProviderCapability.CHAT]
        )
    )

    class DummyLLM(ILLMProvider):
        def supports_model(self, m):
            return m == "qwen2.5-coder"
        async def chat(self, request, **kwargs):
            return ChatResponse(
                message=PromptMessage(role="assistant", content="Synthesizing response context!"),
                finish_reason="stop",
                usage=AIUsage(),
                model=request.model,
                provider="ollama"
            )
        async def stream_chat(self, request, **kwargs):
            pass
        async def health(self):
            pass
        async def available_models(self):
            return []

    provider_registry.register("ollama", DummyLLM())
    factory = ProviderFactory(provider_registry)
    
    gateway = AIGateway(
        provider_registry=provider_registry,
        model_registry=model_registry,
        factory=factory,
        retry_policy=RetryPolicy(),
        timeout_policy=TimeoutPolicy()
    )

    engine = LocalVoiceEngine(gateway=gateway)

    # Execute full voice pipeline using mock command
    audio_cmd = b"Nova, write python login code"
    response = await engine.process_audio_command(audio_cmd)
    
    assert response.text == "Synthesizing response context!"
    assert response.audio_path.endswith(".wav")
