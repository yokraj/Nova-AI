"""Nova-AI Unified Multimodal Input & Command Orchestration Package (Phase 10M-A).

Unifies text, offline Whisper voice, screen vision, and desktop context into a single
canonical execution pipeline.
"""

from app.ai.multimodal.models import (
    ActiveAppContext,
    ClarificationOption,
    ClarificationRequest,
    InputModality,
    IntentCategory,
    InteractionState,
    MultimodalConversationContext,
    MultimodalExecutionResult,
    MultimodalTurn,
    NormalizedMultimodalInput,
    ScreenReference,
    StructuredTaskRequest,
)
from app.ai.multimodal.normalizer import MultimodalInputNormalizer
from app.ai.multimodal.intent_analyzer import MultimodalIntentAnalyzer
from app.ai.multimodal.context_manager import MultimodalContextManager
from app.ai.multimodal.voice_interface import MultimodalVoiceInterface
from app.ai.multimodal.vision_grounding import MultimodalVisionGrounder
from app.ai.multimodal.orchestrator import UnifiedMultimodalOrchestrator

__all__ = [
    "ActiveAppContext",
    "ClarificationOption",
    "ClarificationRequest",
    "InputModality",
    "IntentCategory",
    "InteractionState",
    "MultimodalConversationContext",
    "MultimodalExecutionResult",
    "MultimodalTurn",
    "NormalizedMultimodalInput",
    "ScreenReference",
    "StructuredTaskRequest",
    "MultimodalInputNormalizer",
    "MultimodalIntentAnalyzer",
    "MultimodalContextManager",
    "MultimodalVoiceInterface",
    "MultimodalVisionGrounder",
    "UnifiedMultimodalOrchestrator",
]

