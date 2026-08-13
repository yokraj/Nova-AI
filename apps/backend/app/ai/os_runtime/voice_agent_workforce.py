"""15-Agent Voice Workforce for AI Operating System Background Runtime.
"""

from typing import List
from app.ai.os_runtime.interfaces import IVoiceAgentWorkforce
from app.ai.os_runtime.models import VoiceAgentBlueprint


class VoiceAgentWorkforce(IVoiceAgentWorkforce):
    """Coordinates the 15 dedicated Voice Workforce Agents."""

    def __init__(self) -> None:
        self._agents: List[VoiceAgentBlueprint] = [
            VoiceAgentBlueprint(agent_id="wake_word_agent", name="Wake Word Agent", role="Monitors continuous audio for 'Hey Nova'"),
            VoiceAgentBlueprint(agent_id="speech_rec_agent", name="Speech Recognition Agent", role="Faster Whisper streaming STT"),
            VoiceAgentBlueprint(agent_id="voice_auth_agent", name="Voice Authentication Agent", role="Verifies speaker voice print"),
            VoiceAgentBlueprint(agent_id="noise_reduction_agent", name="Noise Reduction Agent", role="Calibrates mic & suppresses noise"),
            VoiceAgentBlueprint(agent_id="conv_coord_agent", name="Conversation Coordinator Agent", role="Coordinates voice interaction loop"),
            VoiceAgentBlueprint(agent_id="interrupt_agent", name="Interrupt Agent", role="Handles speech barge-in TTS stop"),
            VoiceAgentBlueprint(agent_id="confirmation_agent", name="Confirmation Agent", role="Manages safety confirmation holds"),
            VoiceAgentBlueprint(agent_id="notification_agent", name="Voice Notification Agent", role="Speaks proactive system alerts"),
            VoiceAgentBlueprint(agent_id="streaming_agent", name="Streaming Agent", role="Streams tokens and incremental TTS"),
            VoiceAgentBlueprint(agent_id="session_agent", name="Voice Session Agent", role="Manages active session context stack"),
            VoiceAgentBlueprint(agent_id="context_agent", name="Context Awareness Agent", role="Monitors desktop, IDE, browser context"),
            VoiceAgentBlueprint(agent_id="tts_synthesis_agent", name="Speech Synthesis Agent", role="Synthesizes voice audio waveform"),
            VoiceAgentBlueprint(agent_id="voice_memory_agent", name="Voice Memory Agent", role="Stores long-term conversation memory"),
            VoiceAgentBlueprint(agent_id="heartbeat_agent", name="Heartbeat Agent", role="Monitors runtime health heartbeat"),
            VoiceAgentBlueprint(agent_id="runtime_supervisor_agent", name="Runtime Supervisor Agent", role="Self-healing crash supervisor"),
        ]

    def list_agents(self) -> List[VoiceAgentBlueprint]:
        """Lists active voice workforce agents."""
        return self._agents
