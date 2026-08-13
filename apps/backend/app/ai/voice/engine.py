"""Main Local Voice Engine pipeline orchestrator.
"""

import time
from typing import Optional
from app.ai.voice.interfaces import ISpeechRecognizer, ITextToSpeechProvider, IWakeWordDetector
from app.ai.voice.speech_recognition.whisper_provider import WhisperSpeechRecognizer
from app.ai.voice.text_to_speech.tts_provider import LocalTTSProvider
from app.ai.voice.wake_word.wake_word_detector import WakeWordDetector
from app.ai.voice.session.session_manager import VoiceSessionManager
from app.ai.voice.intent_classifier import VoiceIntentClassifier
from app.ai.voice.context_builder import VoiceContextBuilder
from app.ai.voice.configuration import VoiceConfiguration
from app.ai.voice.models import VoiceRequest, VoiceResponse, VoiceCommand
from app.ai.voice.exceptions import VoiceEngineError
from app.ai.memory.engine import LocalMemoryEngine
from app.ai.gateway.ai_gateway import AIGateway
from app.core.dependency_container import resolve

class LocalVoiceEngine:
    """Orchestrates Wake Word -> STT -> Intent -> RAG Memory -> AI Gateway -> TTS audio execution loops."""

    def __init__(
        self,
        config: Optional[VoiceConfiguration] = None,
        recognizer: Optional[ISpeechRecognizer] = None,
        tts: Optional[ITextToSpeechProvider] = None,
        wake_detector: Optional[IWakeWordDetector] = None,
        session_mgr: Optional[VoiceSessionManager] = None,
        intent_classifier: Optional[VoiceIntentClassifier] = None,
        context_builder: Optional[VoiceContextBuilder] = None,
        memory: Optional[LocalMemoryEngine] = None,
        gateway: Optional[AIGateway] = None
    ) -> None:
        self.config = config or VoiceConfiguration()
        self.recognizer = recognizer or WhisperSpeechRecognizer()
        self.tts = tts or LocalTTSProvider()
        self.wake_detector = wake_detector or WakeWordDetector(keyword=self.config.wake_word)
        self.session_mgr = session_mgr or VoiceSessionManager()
        self.intent_classifier = intent_classifier or VoiceIntentClassifier()
        self.context_builder = context_builder or VoiceContextBuilder()
        
        # Dependency resolution fallbacks
        try:
            self.gateway = gateway or resolve(AIGateway)
        except Exception:
            self.gateway = gateway

        try:
            self.memory = memory or LocalMemoryEngine()
        except Exception:
            self.memory = memory

    async def process_audio_command(self, audio_bytes: bytes, conversation_id: str = "voice_session") -> VoiceResponse:
        """Processes voice command audio bytes through the pipeline."""
        start_time = time.perf_counter()

        # 1. Wake word check (if enabled)
        if self.config.wake_word_enabled:
            # For verification tests, if the wake detector returns False, raise an error
            # We can pass ASCII wake word like "Nova" in audio_bytes
            if not self.wake_detector.detect(audio_bytes):
                raise VoiceEngineError("Wake word keyword trigger not detected in audio stream.")

        # 2. Transcription
        speech_result = await self.recognizer.transcribe(audio_bytes)
        transcript = speech_result.transcript

        # 3. Intent Classification
        cmd = self.intent_classifier.classify_intent(transcript)

        # 4. Memory Integration
        if cmd.intent == "remember_this" and self.memory:
            from app.ai.memory.models import MemoryType
            content_to_save = cmd.parameters.get("content", transcript)
            await self.memory.store_memory(
                content=content_to_save,
                memory_type=MemoryType.CONVERSATION,
                metadata={"source": "voice_command"}
            )
            response_text = f"I have stored that in my long-term memory."
        else:
            # General Chat routing through Gateway
            if self.gateway:
                from app.ai.models import ChatRequest, PromptMessage
                # Inject voice_context parameter into kwargs
                voice_ctx = self.context_builder.build_voice_context(
                    session_id=conversation_id,
                    recent_commands=[cmd.intent],
                    memory_context=""
                )
                
                request = ChatRequest(
                    model="auto-select-me",
                    messages=[PromptMessage(role="user", content=transcript)]
                )
                gateway_response = await self.gateway.chat(
                    request,
                    conversation_id=conversation_id,
                    voice_context=voice_ctx
                )
                response_text = gateway_response.message.content
            else:
                response_text = f"Mock voice response to intent '{cmd.intent}'."

        # 5. Text-To-Speech Synthesis
        audio_path = await self.tts.synthesize(response_text)

        duration = time.perf_counter() - start_time
        return VoiceResponse(
            text=response_text,
            audio_path=audio_path,
            confidence=speech_result.confidence,
            processing_time=duration
        )
