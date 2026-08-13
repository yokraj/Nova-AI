"""Utility functions and dynamic PEP 562 lazy module loader for app.ai.conversation.
"""

import importlib
from typing import Any, Dict

_LAZY_MAP: Dict[str, str] = {
    "ConversationConfiguration": "app.ai.conversation.configuration",
    "EmotionState": "app.ai.conversation.models",
    "PersonalityProfileType": "app.ai.conversation.models",
    "ConversationTurnRole": "app.ai.conversation.models",
    "ConversationState": "app.ai.conversation.models",
    "EmotionMetadata": "app.ai.conversation.models",
    "PersonalityMetadata": "app.ai.conversation.models",
    "ConversationContextSnapshot": "app.ai.conversation.models",
    "ConversationTurn": "app.ai.conversation.models",
    "ClarificationOption": "app.ai.conversation.models",
    "ConversationSession": "app.ai.conversation.models",
    "ConversationResponsePayload": "app.ai.conversation.models",
    "ConversationHealth": "app.ai.conversation.models",
    "ConversationMetrics": "app.ai.conversation.models",
    "IEmotionEngine": "app.ai.conversation.interfaces",
    "IPersonalityEngine": "app.ai.conversation.interfaces",
    "IDialogManager": "app.ai.conversation.interfaces",
    "IInterruptionManager": "app.ai.conversation.interfaces",
    "IStreamingManager": "app.ai.conversation.interfaces",
    "IConversationManager": "app.ai.conversation.interfaces",
    "IUniversalConversationEngine": "app.ai.conversation.interfaces",
    "ConversationEngineError": "app.ai.conversation.exceptions",
    "SessionNotFoundError": "app.ai.conversation.exceptions",
    "EmotionDetectionError": "app.ai.conversation.exceptions",
    "InvalidPersonalityError": "app.ai.conversation.exceptions",
    "InterruptionError": "app.ai.conversation.exceptions",
    "EmotionDetector": "app.ai.conversation.emotion_detector",
    "EmotionEngine": "app.ai.conversation.emotion_engine",
    "PersonalityProfilesCatalog": "app.ai.conversation.personality_profiles",
    "PersonalityEngine": "app.ai.conversation.personality_engine",
    "DialogManager": "app.ai.conversation.dialog_manager",
    "ConversationStateTracker": "app.ai.conversation.conversation_state",
    "ConversationHistoryTracker": "app.ai.conversation.conversation_history",
    "ConversationMemory": "app.ai.conversation.conversation_memory",
    "CognitiveContextTracker": "app.ai.conversation.conversation_context",
    "AdaptiveResponseFormatter": "app.ai.conversation.adaptive_response",
    "ResponseGenerator": "app.ai.conversation.response_generator",
    "ConversationCompressor": "app.ai.conversation.conversation_compressor",
    "FollowupEngine": "app.ai.conversation.followup_engine",
    "ClarificationEngine": "app.ai.conversation.clarification_engine",
    "InterruptionManager": "app.ai.conversation.interruption_manager",
    "StreamingManager": "app.ai.conversation.streaming_manager",
    "SpeechCoordinator": "app.ai.conversation.speech_coordinator",
    "HumanBehaviorEngine": "app.ai.conversation.human_behavior_engine",
    "ConversationLearningEngine": "app.ai.conversation.conversation_learning",
    "ConversationRecoveryEngine": "app.ai.conversation.conversation_recovery",
    "ConversationValidator": "app.ai.conversation.conversation_validator",
    "ConversationMetricsTracker": "app.ai.conversation.metrics",
    "ConversationHealthMonitor": "app.ai.conversation.health",
    "ConversationCache": "app.ai.conversation.cache",
    "MockConversationProvider": "app.ai.conversation.mock_provider",
    "ConversationManager": "app.ai.conversation.conversation_manager",
    "UniversalConversationEngine": "app.ai.conversation.conversation_engine",
}


def lazy_import(name: str) -> Any:
    """Lazy imports a symbol based on the module map.

    Args:
        name: Name of symbol to import.

    Returns:
        The imported symbol object.
    """
    if name in _LAZY_MAP:
        module_path = _LAZY_MAP[name]
        module = importlib.import_module(module_path)
        return getattr(module, name)
    raise AttributeError(f"module 'app.ai.conversation' has no attribute '{name}'")
