"""Conversation Manager keeping thread histories and decision contexts.
"""

import structlog
from typing import Dict, Any, List, Set
from app.ai.collaboration.models import StructuredMessage, MessageType
from app.ai.collaboration.interfaces import IConversationManager

logger = structlog.get_logger("conversation_manager")

class ConversationManager(IConversationManager):
    """Manages active threads, participant lists, unresolved questions and consensus decisions."""

    def __init__(self) -> None:
        self.threads: Dict[str, List[StructuredMessage]] = {}
        self.participants: Dict[str, Set[str]] = {}
        self.decisions: Dict[str, List[Dict[str, Any]]] = {}
        self.questions: Dict[str, Dict[str, str]] = {}  # correlation_id -> {question_id: question_text}

    def record_message(self, message: StructuredMessage) -> None:
        """Stores message into thread records and updates contexts."""
        cid = message.correlation_id
        if cid not in self.threads:
            self.threads[cid] = []
            self.participants[cid] = set()
            self.decisions[cid] = []
            self.questions[cid] = {}

        self.threads[cid].append(message)
        self.participants[cid].add(message.sender)
        if message.receiver and message.receiver != "all":
            self.participants[cid].add(message.receiver)

        # Parse message content
        if message.message_type == MessageType.QUESTION:
            q_id = message.payload.get("question_id") or str(len(self.questions[cid]))
            self.questions[cid][q_id] = message.payload.get("question", "")
        elif message.message_type == MessageType.ANSWER:
            q_id = message.payload.get("question_id")
            if q_id in self.questions[cid]:
                # Question answered, pop it
                self.questions[cid].pop(q_id, None)
        elif message.message_type == MessageType.APPROVAL_RESPONSE:
            if message.payload.get("approved", False):
                self.decisions[cid].append({
                    "decision": message.payload.get("decision", "Approved"),
                    "approver": message.sender,
                    "timestamp": message.timestamp
                })

    def get_thread_history(self, correlation_id: str) -> List[StructuredMessage]:
        """Returns ordered messages belonging to correlation thread."""
        return self.threads.get(correlation_id, [])

    def get_participants(self, correlation_id: str) -> List[str]:
        """Returns participant list in active conversation."""
        return list(self.participants.get(correlation_id, []))

    def get_decisions(self, correlation_id: str) -> List[Dict[str, Any]]:
        """Returns logged decisions."""
        return self.decisions.get(correlation_id, [])

    def get_unresolved_questions(self, correlation_id: str) -> List[str]:
        """Returns unresolved thread questions list."""
        return list(self.questions.get(correlation_id, {}).values())
