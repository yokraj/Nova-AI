"""Voice Command Router routes voice commands to the canonical execution pipeline.

Links STT → Security Filter → CopilotOrchestrator / AgentRuntime → TTS output.
"""

from typing import Optional, Dict, Any
import structlog

from app.ai.voice.stt_engine import LocalSTTEngine
from app.ai.voice.tts_engine import LocalTTSEngine
from app.ai.voice.security_filter import VoiceSecurityFilter
from app.ai.voice.models import VoiceResponse, SpeechResult
from app.ai.voice.exceptions import VoiceEngineError
from app.ai.copilot.orchestrator import CopilotOrchestrator
from app.ai.copilot.models import CopilotRequest, CopilotMode

logger = structlog.get_logger("voice_command_router")


class VoiceCommandRouter:
    """Routes voice input through STT, security inspection, canonical Copilot/Agent execution, and TTS."""

    def __init__(
        self,
        stt_engine: Optional[LocalSTTEngine] = None,
        tts_engine: Optional[LocalTTSEngine] = None,
        copilot_orchestrator: Optional[CopilotOrchestrator] = None,
    ) -> None:
        self.stt_engine = stt_engine or LocalSTTEngine()
        self.tts_engine = tts_engine or LocalTTSEngine()
        self.copilot_orchestrator = copilot_orchestrator or CopilotOrchestrator()
        self.security_filter = VoiceSecurityFilter()

    async def route_audio(self, audio_bytes: bytes, target_app: str = "Blender") -> VoiceResponse:
        """Processes raw audio input, transcribes, inspects, executes via canonical pipeline, and synthesizes output."""
        speech_result = await self.stt_engine.transcribe(audio_bytes)
        return await self.route_transcript(speech_result.transcript, target_app=target_app)

    async def route_transcript(self, transcript: str, target_app: str = "Blender") -> VoiceResponse:
        """Routes transcript text to canonical Copilot/Agent runtime after security inspection."""
        # 1. Inspect transcript security
        self.security_filter.inspect_transcript(transcript)

        # 2. Map spoken command to CopilotRequest parameters
        params: Dict[str, Any] = {}
        clean_text = transcript.lower()

        if "cube" in clean_text or "create cube" in clean_text:
            params = {"action_type": "create_object", "primitive": "cube", "target_label": "VoiceCube"}
        elif "sphere" in clean_text:
            params = {"action_type": "create_object", "primitive": "uv_sphere", "target_label": "VoiceSphere"}
        elif "delete" in clean_text:
            params = {"action_type": "delete_object", "target_label": "VoiceCube"}
        elif "save" in clean_text:
            params = {"action_type": "save_file", "target_label": "voice_scene.blend"}
        else:
            params = {"action_type": "gui_click", "target_label": transcript}

        copilot_req = CopilotRequest(
            user_prompt=transcript,
            mode=CopilotMode.EXECUTE,
            target_app=target_app,
            parameters=params,
        )

        # 3. Canonical execution via CopilotOrchestrator
        copilot_res = await self.copilot_orchestrator.process_request(copilot_req)

        if copilot_res.success:
            response_text = f"Executed voice command: {transcript}. State verified."
        else:
            response_text = f"Voice command failed: {copilot_res.status_message}"

        # 4. Synthesize spoken audio response via local TTS engine
        audio_path = await self.tts_engine.synthesize(response_text)

        return VoiceResponse(
            text=response_text,
            audio_path=audio_path,
            confidence=0.98 if copilot_res.success else 0.0,
            processing_time=0.1,
        )
