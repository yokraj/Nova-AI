"""Human-Like Conversation, Emotional Intelligence & Cognitive Interaction Engine package.

Exposes configuration, models, interfaces, exceptions, EmotionEngine, PersonalityEngine, DialogManager,
FollowupEngine, ClarificationEngine, InterruptionManager, StreamingManager, SpeechCoordinator,
HumanBehaviorEngine, ConversationLearningEngine, observability, and central UniversalConversationEngine.
"""

import sys
from typing import Any
from app.ai.conversation.utils import lazy_import

__all__ = [
    "ConversationConfiguration",
    "EmotionState",
    "PersonalityProfileType",
    "ConversationTurnRole",
    "ConversationState",
    "EmotionMetadata",
    "PersonalityMetadata",
    "ConversationContextSnapshot",
    "ConversationTurn",
    "ClarificationOption",
    "ConversationSession",
    "ConversationResponsePayload",
    "ConversationHealth",
    "ConversationMetrics",
    "IEmotionEngine",
    "IPersonalityEngine",
    "IDialogManager",
    "IInterruptionManager",
    "IStreamingManager",
    "IConversationManager",
    "IUniversalConversationEngine",
    "ConversationEngineError",
    "SessionNotFoundError",
    "EmotionDetectionError",
    "InvalidPersonalityError",
    "InterruptionError",
    "EmotionDetector",
    "EmotionEngine",
    "PersonalityProfilesCatalog",
    "PersonalityEngine",
    "DialogManager",
    "ConversationStateTracker",
    "ConversationHistoryTracker",
    "ConversationMemory",
    "CognitiveContextTracker",
    "AdaptiveResponseFormatter",
    "ResponseGenerator",
    "ConversationCompressor",
    "FollowupEngine",
    "ClarificationEngine",
    "InterruptionManager",
    "StreamingManager",
    "SpeechCoordinator",
    "HumanBehaviorEngine",
    "ConversationLearningEngine",
    "ConversationRecoveryEngine",
    "ConversationValidator",
    "ConversationMetricsTracker",
    "ConversationHealthMonitor",
    "ConversationCache",
    "MockConversationProvider",
    "ConversationManager",
    "UniversalConversationEngine",
]


def __getattr__(name: str) -> Any:
    return lazy_import(name)
