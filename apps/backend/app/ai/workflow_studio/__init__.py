"""Universal Workflow Learning, Recording & No-Code Automation Studio package.

Exposes configuration, models, interfaces, exceptions, recorder suite, intent extractor, workflow builder, player,
editor, variable engine, trigger engine, marketplace, observability, and UniversalWorkflowStudioEngine.
"""

import sys
from typing import Any
from app.ai.workflow_studio.utils import lazy_import

__all__ = [
    "WorkflowStudioConfiguration",
    "WorkflowRecordingState",
    "WorkflowTriggerType",
    "WorkflowActionType",
    "RecordedEvent",
    "WorkflowVariable",
    "WorkflowTrigger",
    "WorkflowStep",
    "WorkflowDefinition",
    "WorkflowExecutionResult",
    "WorkflowStudioHealth",
    "WorkflowStudioMetrics",
    "IWorkflowRecorder",
    "IIntentExtractor",
    "IVariableEngine",
    "IWorkflowPlayer",
    "IWorkflowStudioManager",
    "IUniversalWorkflowStudioEngine",
    "WorkflowStudioError",
    "RecordingError",
    "ExecutionError",
    "ValidationError",
    "ImportExportError",
    "WorkflowRecorder",
    "DesktopRecorder",
    "BrowserRecorder",
    "KeyboardRecorder",
    "MouseRecorder",
    "VoiceRecorder",
    "EventStream",
    "IntentExtractor",
    "WorkflowBuilder",
    "WorkflowEditor",
    "WorkflowOptimizer",
    "WorkflowValidator",
    "WorkflowPlayer",
    "WorkflowTemplates",
    "MacroConverter",
    "ParameterEngine",
    "VariableEngine",
    "ConditionEngine",
    "LoopEngine",
    "TriggerEngine",
    "Scheduler",
    "WorkflowDebugger",
    "WorkflowExporter",
    "WorkflowImporter",
    "WorkflowMarketplace",
    "WorkflowSharing",
    "WorkflowVersioning",
    "WorkflowSecurity",
    "WorkflowRecovery",
    "WorkflowLearning",
    "RecommendationEngine",
    "WorkflowStudioMetricsTracker",
    "WorkflowStudioHealthMonitor",
    "WorkflowStudioCache",
    "MockWorkflowStudioProvider",
    "WorkflowStudioManager",
    "UniversalWorkflowStudioEngine",
]


def __getattr__(name: str) -> Any:
    return lazy_import(name)
