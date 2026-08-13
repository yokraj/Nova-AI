"""Abstract base contracts for Universal Workflow Learning & No-Code Automation Studio.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.ai.workflow_studio.models import (
    RecordedEvent,
    WorkflowDefinition,
    WorkflowExecutionResult,
    WorkflowStep,
    WorkflowStudioHealth,
    WorkflowStudioMetrics,
    WorkflowVariable,
)


class IWorkflowRecorder(ABC):
    """Workflow Recorder contract for starting, pausing, and stopping event recording."""

    @abstractmethod
    def start_recording(self, session_name: str) -> str:
        """Starts recording session."""
        pass

    @abstractmethod
    def stop_recording(self) -> List[RecordedEvent]:
        """Stops recording session and returns recorded events."""
        pass


class IIntentExtractor(ABC):
    """Intent Extractor contract for converting raw events into high-level steps."""

    @abstractmethod
    def extract_intents(self, events: List[RecordedEvent]) -> List[WorkflowStep]:
        """Converts low-level events into semantic workflow steps."""
        pass


class IVariableEngine(ABC):
    """Variable Engine contract for detecting dynamic input variables."""

    @abstractmethod
    def detect_variables(self, text: str) -> List[WorkflowVariable]:
        """Detects variables (emails, OTPs, amounts, passwords) in text."""
        pass


class IWorkflowPlayer(ABC):
    """Workflow Player contract for executing recorded workflow definitions."""

    @abstractmethod
    async def play_workflow(self, workflow_id: str, parameters: Optional[Dict[str, Any]] = None) -> WorkflowExecutionResult:
        """Executes workflow definition."""
        pass


class IWorkflowStudioManager(ABC):
    """Subsystem Manager administrative contract."""

    @abstractmethod
    async def start(self) -> None:
        """Starts workflow studio manager."""
        pass


class IUniversalWorkflowStudioEngine(ABC):
    """Central Universal Workflow Studio Engine facade contract."""

    @abstractmethod
    async def record_workflow(self, name: str) -> Dict[str, Any]:
        """Starts recording a new workflow session."""
        pass

    @abstractmethod
    async def stop_recording(self) -> Dict[str, Any]:
        """Stops active recording session and returns created workflow definition."""
        pass

    @abstractmethod
    async def play_workflow(self, workflow_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes workflow by ID or name."""
        pass

    @abstractmethod
    async def edit_workflow(self, workflow_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Edits an existing workflow definition."""
        pass

    @abstractmethod
    async def delete_workflow(self, workflow_id: str) -> bool:
        """Deletes a workflow definition."""
        pass

    @abstractmethod
    async def list_workflows(self) -> List[Dict[str, Any]]:
        """Lists all registered workflow definitions."""
        pass

    @abstractmethod
    async def export_workflow(self, workflow_id: str, format_type: str = "json") -> str:
        """Exports workflow definition to file format."""
        pass

    @abstractmethod
    async def import_workflow(self, content: str, format_type: str = "json") -> Dict[str, Any]:
        """Imports workflow definition from string content."""
        pass

    @abstractmethod
    async def share_workflow(self, workflow_id: str, target: str = "community") -> Dict[str, Any]:
        """Shares workflow to marketplace or community."""
        pass

    @abstractmethod
    async def workflow_history(self) -> List[Dict[str, Any]]:
        """Retrieves workflow execution history log."""
        pass
