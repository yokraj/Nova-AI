"""Voice Context Builder builds prompt contexts.
"""

from typing import Dict, Any, List

class VoiceContextBuilder:
    """Consolidates current listener sessions, user preferences, and memories contexts."""

    def build_voice_context(
        self,
        session_id: str,
        recent_commands: List[str],
        memory_context: str
    ) -> Dict[str, Any]:
        """Assembles context package containing current session and memory parameters."""
        return {
            "session_id": session_id,
            "recent_commands": recent_commands,
            "memory_context": memory_context,
            "active_workflow": "voice_control"
        }
