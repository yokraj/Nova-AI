"""Utility functions and dynamic PEP 562 lazy module loader for app.ai.workflow_studio.
"""

import importlib
import re
from typing import Any, Dict, List

_LAZY_MAP: Dict[str, str] = {
    "WorkflowStudioConfiguration": "app.ai.workflow_studio.configuration",
    "WorkflowRecordingState": "app.ai.workflow_studio.models",
    "WorkflowTriggerType": "app.ai.workflow_studio.models",
    "WorkflowActionType": "app.ai.workflow_studio.models",
    "RecordedEvent": "app.ai.workflow_studio.models",
    "WorkflowVariable": "app.ai.workflow_studio.models",
    "WorkflowTrigger": "app.ai.workflow_studio.models",
    "WorkflowStep": "app.ai.workflow_studio.models",
    "WorkflowDefinition": "app.ai.workflow_studio.models",
    "WorkflowExecutionResult": "app.ai.workflow_studio.models",
    "WorkflowStudioHealth": "app.ai.workflow_studio.models",
    "WorkflowStudioMetrics": "app.ai.workflow_studio.models",
    "IWorkflowRecorder": "app.ai.workflow_studio.interfaces",
    "IIntentExtractor": "app.ai.workflow_studio.interfaces",
    "IVariableEngine": "app.ai.workflow_studio.interfaces",
    "IWorkflowPlayer": "app.ai.workflow_studio.interfaces",
    "IWorkflowStudioManager": "app.ai.workflow_studio.interfaces",
    "IUniversalWorkflowStudioEngine": "app.ai.workflow_studio.interfaces",
    "WorkflowStudioError": "app.ai.workflow_studio.exceptions",
    "RecordingError": "app.ai.workflow_studio.exceptions",
    "ExecutionError": "app.ai.workflow_studio.exceptions",
    "ValidationError": "app.ai.workflow_studio.exceptions",
    "ImportExportError": "app.ai.workflow_studio.exceptions",
    "WorkflowRecorder": "app.ai.workflow_studio.workflow_recorder",
    "DesktopRecorder": "app.ai.workflow_studio.desktop_recorder",
    "BrowserRecorder": "app.ai.workflow_studio.browser_recorder",
    "KeyboardRecorder": "app.ai.workflow_studio.keyboard_recorder",
    "MouseRecorder": "app.ai.workflow_studio.mouse_recorder",
    "VoiceRecorder": "app.ai.workflow_studio.voice_recorder",
    "EventStream": "app.ai.workflow_studio.event_stream",
    "IntentExtractor": "app.ai.workflow_studio.intent_extractor",
    "WorkflowBuilder": "app.ai.workflow_studio.workflow_builder",
    "WorkflowEditor": "app.ai.workflow_studio.workflow_editor",
    "WorkflowOptimizer": "app.ai.workflow_studio.workflow_optimizer",
    "WorkflowValidator": "app.ai.workflow_studio.workflow_validator",
    "WorkflowPlayer": "app.ai.workflow_studio.workflow_player",
    "WorkflowTemplates": "app.ai.workflow_studio.workflow_templates",
    "MacroConverter": "app.ai.workflow_studio.macro_converter",
    "ParameterEngine": "app.ai.workflow_studio.parameter_engine",
    "VariableEngine": "app.ai.workflow_studio.variable_engine",
    "ConditionEngine": "app.ai.workflow_studio.condition_engine",
    "LoopEngine": "app.ai.workflow_studio.loop_engine",
    "TriggerEngine": "app.ai.workflow_studio.trigger_engine",
    "Scheduler": "app.ai.workflow_studio.scheduler",
    "WorkflowDebugger": "app.ai.workflow_studio.workflow_debugger",
    "WorkflowExporter": "app.ai.workflow_studio.workflow_exporter",
    "WorkflowImporter": "app.ai.workflow_studio.workflow_importer",
    "WorkflowMarketplace": "app.ai.workflow_studio.workflow_marketplace",
    "WorkflowSharing": "app.ai.workflow_studio.workflow_sharing",
    "WorkflowVersioning": "app.ai.workflow_studio.workflow_versioning",
    "WorkflowSecurity": "app.ai.workflow_studio.workflow_security",
    "WorkflowRecovery": "app.ai.workflow_studio.workflow_recovery",
    "WorkflowLearning": "app.ai.workflow_studio.workflow_learning",
    "RecommendationEngine": "app.ai.workflow_studio.recommendation_engine",
    "WorkflowStudioMetricsTracker": "app.ai.workflow_studio.metrics",
    "WorkflowStudioHealthMonitor": "app.ai.workflow_studio.health",
    "WorkflowStudioCache": "app.ai.workflow_studio.cache",
    "MockWorkflowStudioProvider": "app.ai.workflow_studio.mock_provider",
    "WorkflowStudioManager": "app.ai.workflow_studio.manager",
    "UniversalWorkflowStudioEngine": "app.ai.workflow_studio.engine",
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
    raise AttributeError(f"module 'app.ai.workflow_studio' has no attribute '{name}'")


def extract_regex_matches(text: str, pattern: str) -> List[str]:
    """Helper utility extracting regex matches from text."""
    return re.findall(pattern, text)
