"""Intent Classifier categorizes voice commands.
"""

from typing import Dict, Any
from app.ai.voice.models import VoiceCommand

class VoiceIntentClassifier:
    """Classifies spoken text commands into intents matching agent capabilities."""

    def classify_intent(self, transcript: str) -> VoiceCommand:
        """Heuristically maps transcription string to command actions."""
        text = transcript.lower()

        if "remember" in text or "store" in text or "save" in text:
            return VoiceCommand(
                command_type="memory",
                intent="remember_this",
                parameters={"content": transcript.replace("remember this", "").strip()}
            )
        elif "fix" in text or "bug" in text or "error" in text:
            return VoiceCommand(
                command_type="software_engineer",
                intent="debugging",
                parameters={"query": transcript}
            )
        elif "analyze" in text or "code" in text or "explain" in text:
            return VoiceCommand(
                command_type="software_engineer",
                intent="code_intelligence",
                parameters={"query": transcript}
            )
        elif "document" in text or "documentation" in text:
            return VoiceCommand(
                command_type="software_engineer",
                intent="documentation",
                parameters={"query": transcript}
            )
        elif "open" in text or "project" in text:
            return VoiceCommand(
                command_type="software_engineer",
                intent="project_manager",
                parameters={"query": transcript}
            )
        else:
            return VoiceCommand(
                command_type="chat",
                intent="general_conversation",
                parameters={"query": transcript}
            )
