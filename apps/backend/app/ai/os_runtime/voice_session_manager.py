"""Voice Session Manager tracking conversation history, active missions, and project context stack.
"""

from typing import Any, Dict, List, Optional


class VoiceSessionManager:
    """Manages active user session stack, active workspace, IDE project, browser tabs, and mission confirmations."""

    def __init__(self) -> None:
        self.session_id: str = "sess_voice_primary"
        self.active_workspace: str = "Nova Monorepo"
        self.active_project: str = "Nova-AI"
        self.active_mission_id: Optional[str] = None
        self.conversation_history: List[Dict[str, str]] = []
        self.pending_confirmations: Dict[str, Any] = {}

    def record_turn(self, role: str, content: str) -> None:
        self.conversation_history.append({"role": role, "content": content})

    def get_context_snapshot(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "active_workspace": self.active_workspace,
            "active_project": self.active_project,
            "active_mission_id": self.active_mission_id,
            "history_turns_count": len(self.conversation_history),
        }
