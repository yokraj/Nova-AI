"""Context Manager for Nova-AI Multimodal Interactions.

Maintains task-specific conversation history, active execution states, and session isolation.
"""

from typing import Dict, List, Optional
import threading
import time
import uuid
import structlog

from app.ai.multimodal.models import (
    ClarificationRequest,
    InteractionState,
    MultimodalConversationContext,
    MultimodalTurn,
    StructuredTaskRequest,
)

logger = structlog.get_logger("multimodal_context_manager")


class MultimodalContextManager:
    """Manages conversation context, state isolation, and multi-turn task history."""

    def __init__(self) -> None:
        self._contexts: Dict[str, MultimodalConversationContext] = {}
        self._lock = threading.RLock()

    def get_or_create_context(self, session_id: Optional[str] = None) -> MultimodalConversationContext:
        """Retrieves an existing context or creates a new isolated session context."""
        sid = session_id or f"session_{uuid.uuid4().hex[:8]}"
        with self._lock:
            if sid not in self._contexts:
                self._contexts[sid] = MultimodalConversationContext(
                    session_id=sid,
                    state=InteractionState.IDLE,
                )
            return self._contexts[sid]

    def record_turn(
        self,
        session_id: str,
        user_text: str,
        modality: Any,
        status: str = "completed",
        task_request: Optional[StructuredTaskRequest] = None,
        agent_response_text: str = "",
        tts_audio_path: Optional[str] = None,
    ) -> MultimodalTurn:
        """Appends a new interaction turn to the target session context."""
        turn = MultimodalTurn(
            turn_id=f"turn_{uuid.uuid4().hex[:8]}",
            timestamp=time.time(),
            modality=modality,
            user_text=user_text,
            task_request=task_request,
            status=status,
            agent_response_text=agent_response_text,
            tts_audio_path=tts_audio_path,
        )

        with self._lock:
            ctx = self._contexts.get(session_id)
            if ctx is None:
                ctx = MultimodalConversationContext(session_id=session_id)
                self._contexts[session_id] = ctx

            ctx.turns.append(turn)
            if task_request:
                ctx.last_task_request = task_request
                if task_request.target_app and task_request.target_app != "System":
                    ctx.active_app = task_request.target_app

        return turn

    def set_active_task(self, session_id: str, task_id: str, app_name: Optional[str] = None) -> None:
        """Updates the active task ID and target application for a session."""
        with self._lock:
            ctx = self.get_or_create_context(session_id)
            ctx.active_task_id = task_id
            if app_name:
                ctx.active_app = app_name

    def set_pending_clarification(self, session_id: str, request: ClarificationRequest) -> None:
        """Stores a pending clarification request requiring user input."""
        with self._lock:
            ctx = self.get_or_create_context(session_id)
            ctx.pending_clarification = request
            ctx.state = InteractionState.AWAITING_CLARIFICATION

    def get_pending_clarification(self, session_id: str) -> Optional[ClarificationRequest]:
        """Retrieves the pending clarification request if one exists."""
        with self._lock:
            ctx = self._contexts.get(session_id)
            return ctx.pending_clarification if ctx else None

    def clear_pending_clarification(self, session_id: str) -> Optional[ClarificationRequest]:
        """Clears and returns any pending clarification request for the session."""
        with self._lock:
            ctx = self._contexts.get(session_id)
            if ctx and ctx.pending_clarification:
                req = ctx.pending_clarification
                ctx.pending_clarification = None
                return req
            return None

    def set_state(self, session_id: str, state: InteractionState) -> None:
        """Sets the current lifecycle state for the session."""
        with self._lock:
            ctx = self.get_or_create_context(session_id)
            ctx.state = state

    def clear_session(self, session_id: str) -> None:
        """Cleans up and removes all context for target session."""
        with self._lock:
            if session_id in self._contexts:
                del self._contexts[session_id]
