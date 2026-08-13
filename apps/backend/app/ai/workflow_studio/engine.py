"""Central Universal Workflow Studio Engine facade unifying recording, intent extraction, editing, and playback.
"""

import time
from typing import Any, Dict, List, Optional
from app.ai.workflow_studio.browser_recorder import BrowserRecorder
from app.ai.workflow_studio.cache import WorkflowStudioCache
from app.ai.workflow_studio.condition_engine import ConditionEngine
from app.ai.workflow_studio.configuration import WorkflowStudioConfiguration
from app.ai.workflow_studio.desktop_recorder import DesktopRecorder
from app.ai.workflow_studio.event_stream import EventStream
from app.ai.workflow_studio.health import WorkflowStudioHealthMonitor
from app.ai.workflow_studio.intent_extractor import IntentExtractor
from app.ai.workflow_studio.interfaces import IUniversalWorkflowStudioEngine
from app.ai.workflow_studio.keyboard_recorder import KeyboardRecorder
from app.ai.workflow_studio.loop_engine import LoopEngine
from app.ai.workflow_studio.macro_converter import MacroConverter
from app.ai.workflow_studio.manager import WorkflowStudioManager
from app.ai.workflow_studio.metrics import WorkflowStudioMetricsTracker
from app.ai.workflow_studio.models import (
    WorkflowDefinition,
    WorkflowExecutionResult,
    WorkflowRecordingState,
    WorkflowStudioHealth,
    WorkflowStudioMetrics,
)
from app.ai.workflow_studio.mouse_recorder import MouseRecorder
from app.ai.workflow_studio.parameter_engine import ParameterEngine
from app.ai.workflow_studio.recommendation_engine import RecommendationEngine
from app.ai.workflow_studio.scheduler import Scheduler
from app.ai.workflow_studio.trigger_engine import TriggerEngine
from app.ai.workflow_studio.variable_engine import VariableEngine
from app.ai.workflow_studio.voice_recorder import VoiceRecorder
from app.ai.workflow_studio.workflow_builder import WorkflowBuilder
from app.ai.workflow_studio.workflow_debugger import WorkflowDebugger
from app.ai.workflow_studio.workflow_editor import WorkflowEditor
from app.ai.workflow_studio.workflow_exporter import WorkflowExporter
from app.ai.workflow_studio.workflow_importer import WorkflowImporter
from app.ai.workflow_studio.workflow_learning import WorkflowLearning
from app.ai.workflow_studio.workflow_marketplace import WorkflowMarketplace
from app.ai.workflow_studio.workflow_optimizer import WorkflowOptimizer
from app.ai.workflow_studio.workflow_player import WorkflowPlayer
from app.ai.workflow_studio.workflow_recorder import WorkflowRecorder
from app.ai.workflow_studio.workflow_recovery import WorkflowRecovery
from app.ai.workflow_studio.workflow_security import WorkflowSecurity
from app.ai.workflow_studio.workflow_sharing import WorkflowSharing
from app.ai.workflow_studio.workflow_templates import WorkflowTemplates
from app.ai.workflow_studio.workflow_validator import WorkflowValidator
from app.ai.workflow_studio.workflow_versioning import WorkflowVersioning


class UniversalWorkflowStudioEngine(IUniversalWorkflowStudioEngine):
    """The central Universal Workflow Studio Platform runtime for Nova AI."""

    def __init__(self, config: Optional[WorkflowStudioConfiguration] = None) -> None:
        self.config = config or WorkflowStudioConfiguration()
        self.manager = WorkflowStudioManager(self.config)

        self.recorder = WorkflowRecorder()
        self.desktop_recorder = DesktopRecorder()
        self.browser_recorder = BrowserRecorder()
        self.keyboard_recorder = KeyboardRecorder()
        self.mouse_recorder = MouseRecorder()
        self.voice_recorder = VoiceRecorder()
        self.event_stream = EventStream()

        self.intent_extractor = IntentExtractor()
        self.workflow_builder = WorkflowBuilder()
        self.workflow_editor = WorkflowEditor()
        self.workflow_optimizer = WorkflowOptimizer()
        self.workflow_validator = WorkflowValidator()
        self.workflow_player = WorkflowPlayer()
        self.workflow_templates = WorkflowTemplates()
        self.macro_converter = MacroConverter()

        self.parameter_engine = ParameterEngine()
        self.variable_engine = VariableEngine()
        self.condition_engine = ConditionEngine()
        self.loop_engine = LoopEngine()
        self.trigger_engine = TriggerEngine()
        self.scheduler = Scheduler()
        self.workflow_debugger = WorkflowDebugger()

        self.exporter = WorkflowExporter()
        self.importer = WorkflowImporter()
        self.marketplace = WorkflowMarketplace()
        self.sharing = WorkflowSharing()
        self.versioning = WorkflowVersioning()
        self.security = WorkflowSecurity()
        self.recovery = WorkflowRecovery()
        self.workflow_learning = WorkflowLearning()
        self.recommendation_engine = RecommendationEngine()

        self.metrics_tracker = WorkflowStudioMetricsTracker()
        self.health_monitor = WorkflowStudioHealthMonitor()
        self.cache = WorkflowStudioCache(ttl_seconds=self.config.cache_ttl_seconds)

        self._registered_workflows: Dict[str, WorkflowDefinition] = {}
        self._execution_history: List[WorkflowExecutionResult] = []

        # Populate pre-built template workflows
        for tmpl in self.workflow_templates.get_template_catalog():
            self._registered_workflows[tmpl.workflow_id] = tmpl

    async def record_workflow(self, name: str) -> Dict[str, Any]:
        """Starts recording a new workflow session."""
        sess = self.recorder.start_recording(name)
        self.metrics_tracker.record_session()

        # Simulate recording sample events
        evt_click = self.mouse_recorder.capture_click(100, 200, "Submit Orders Button", app_name="Dashboard")
        evt_type = self.keyboard_recorder.capture_typing("user@example.com $1,250.00 OTP 123456", app_name="Dashboard")
        self.recorder.record_event(evt_click)
        self.recorder.record_event(evt_type)
        self.event_stream.push_event(evt_click)
        self.event_stream.push_event(evt_type)

        return {"status": "RECORDING", "session_name": sess, "state": self.recorder.state.value}

    async def stop_recording(self) -> Dict[str, Any]:
        """Stops active recording session, extracts intents and variables, and creates workflow definition."""
        events = self.recorder.stop_recording()
        steps = self.intent_extractor.extract_intents(events)

        # Detect variables in typed text events
        all_text = " ".join([e.text_value for e in events if e.text_value])
        vars_detected = self.variable_engine.detect_variables(all_text)
        for _ in vars_detected:
            self.metrics_tracker.record_variable_detected()

        # Create voice trigger
        trigger = self.trigger_engine.create_voice_trigger("Hey Nova, execute recorded workflow")

        wf = self.workflow_builder.build_workflow("New Recorded Workflow", steps, variables=vars_detected, triggers=[trigger])
        wf = self.workflow_optimizer.optimize_definition(wf)
        self._registered_workflows[wf.workflow_id] = wf

        self.metrics_tracker.record_workflow_created()
        return wf.model_dump(mode="json")

    async def play_workflow(self, workflow_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes workflow definition by ID or name."""
        target_wf = self._registered_workflows.get(workflow_id)
        if not target_wf:
            # Fallback search by name
            for wf in self._registered_workflows.values():
                if wf.name.lower() == workflow_id.lower():
                    target_wf = wf
                    break

        target_id = target_wf.workflow_id if target_wf else workflow_id
        if target_wf and parameters:
            target_wf = self.parameter_engine.bind_parameters(target_wf, parameters)

        result = await self.workflow_player.play_workflow(target_id, parameters=parameters)
        self._execution_history.append(result)
        self.metrics_tracker.record_execution()
        return result.model_dump(mode="json")

    async def edit_workflow(self, workflow_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Edits an existing workflow definition."""
        wf = self._registered_workflows.get(workflow_id)
        if not wf:
            raise KeyError(f"Workflow '{workflow_id}' not found.")
        if "name" in updates:
            wf.name = updates["name"]
        if "description" in updates:
            wf.description = updates["description"]
        wf = self.versioning.increment_version(wf)
        return wf.model_dump(mode="json")

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Deletes a workflow definition."""
        if workflow_id in self._registered_workflows:
            del self._registered_workflows[workflow_id]
            return True
        return False

    async def list_workflows(self) -> List[Dict[str, Any]]:
        """Lists all registered workflow definitions."""
        return [wf.model_dump(mode="json") for wf in self._registered_workflows.values()]

    async def export_workflow(self, workflow_id: str, format_type: str = "json") -> str:
        """Exports workflow definition to file format."""
        wf = self._registered_workflows.get(workflow_id) or list(self._registered_workflows.values())[0]
        return self.exporter.export_to_json(wf)

    async def import_workflow(self, content: str, format_type: str = "json") -> Dict[str, Any]:
        """Imports workflow definition from string content."""
        wf = self.importer.import_from_json(content)
        self._registered_workflows[wf.workflow_id] = wf
        return wf.model_dump(mode="json")

    async def share_workflow(self, workflow_id: str, target: str = "community") -> Dict[str, Any]:
        """Shares workflow to marketplace or community."""
        wf = self._registered_workflows.get(workflow_id) or list(self._registered_workflows.values())[0]
        return self.sharing.share_with_user(wf, f"{target}@nova-ai.org")

    async def workflow_history(self) -> List[Dict[str, Any]]:
        """Retrieves workflow execution history log."""
        return [e.model_dump(mode="json") for e in self._execution_history]

    async def check_health(self) -> WorkflowStudioHealth:
        """Retrieves workflow studio health diagnostics."""
        active = 1 if self.recorder.state == WorkflowRecordingState.RECORDING else 0
        return self.health_monitor.check_health(len(self._registered_workflows), active)

    async def get_metrics(self) -> WorkflowStudioMetrics:
        """Retrieves telemetry metrics."""
        return self.metrics_tracker.get_metrics()
