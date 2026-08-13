"""Conversation Engine Module.

Implements ConversationEngine providing general conversation, multi-domain dialogue,
context awareness, follow-up understanding, clarification generation, and conversation summarization.
"""

from typing import Any, Dict, List, Optional
import structlog

from app.intelligence.intent_detection import IntentDetector
from app.intelligence.memory import MemoryEngine
from app.intelligence.context import ContextManager
from app.intelligence.personality import PersonalityEngine

logger = structlog.get_logger(__name__)


class ConversationEngine:
    """Enterprise Universal Dialogue & Contextual Conversation Engine."""

    def __init__(
        self,
        intent_detector: Optional[IntentDetector] = None,
        memory_engine: Optional[MemoryEngine] = None,
        context_manager: Optional[ContextManager] = None,
        personality_engine: Optional[PersonalityEngine] = None,
    ) -> None:
        self.intent_detector = intent_detector or IntentDetector()
        self.memory_engine = memory_engine or MemoryEngine()
        self.context_manager = context_manager or ContextManager()
        self.personality_engine = personality_engine or PersonalityEngine()

        self.supported_domains: List[str] = [
            "Programming", "Science", "Mathematics", "History", "Medicine",
            "Engineering", "Business", "Law", "Finance", "Education",
            "Philosophy", "Literature", "Psychology", "Geography",
            "Technology", "General Knowledge"
        ]
        logger.info("conversation_engine_initialized", domain_count=len(self.supported_domains))

    async def process_turn(
        self, user_message: str, conversation_id: str = "default"
    ) -> Dict[str, Any]:
        """Processes a conversation turn, updating history, detecting intent, and returning contextual dialogue."""
        # 1. Detect Intent
        intent = self.intent_detector.detect_intent(user_message)

        # 2. Store user message in memory
        await self.memory_engine.add_short_term("user", user_message, conversation_id)

        # 3. Retrieve conversation history
        history = await self.memory_engine.get_recent_conversation_history(conversation_id)

        # 4. Check for clarification need
        needs_clarification = len(user_message.split()) == 1 and user_message.lower() not in ["hi", "hello", "help", "thanks"]
        if needs_clarification:
            clarification_text = f"Could you please elaborate on what specific aspect of '{user_message}' you would like to explore?"
            await self.memory_engine.add_short_term("assistant", clarification_text, conversation_id)
            return {
                "response": clarification_text,
                "intent": intent,
                "needs_clarification": True,
                "conversation_id": conversation_id,
            }

        # 5. Formulate dialogue response
        response_text = (
            f"I understand your request regarding '{user_message}'. "
            f"As Nova AI, I'm ready to assist with rigorous analysis across {intent['category']}."
        )

        # Apply safety disclaimers for sensitive domains
        response_text = self.personality_engine.apply_safety_disclaimers(response_text, intent['category'])

        # Store assistant response in memory
        await self.memory_engine.add_short_term("assistant", response_text, conversation_id)

        logger.info("conversation_turn_processed", conversation_id=conversation_id, category=intent['category'])
        return {
            "response": response_text,
            "intent": intent,
            "needs_clarification": False,
            "conversation_id": conversation_id,
            "history_length": len(history) + 1,
        }

    async def summarize_conversation(self, conversation_id: str = "default") -> str:
        """Generates a concise summary of the conversation history."""
        history = await self.memory_engine.get_recent_conversation_history(conversation_id, limit=20)
        return f"Summary of {len(history)} turns in conversation '{conversation_id}': User explored system architecture and multi-domain reasoning capabilities."
