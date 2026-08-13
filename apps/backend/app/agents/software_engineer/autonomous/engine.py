"""LocalAutonomousEngine implements IAutonomousEngine, coordinating the 15-stage workflow.
"""

import os
from typing import Any, Optional
from datetime import datetime

from app.agents.software_engineer.autonomous.interfaces import IAutonomousEngine
from app.agents.software_engineer.autonomous.exceptions import AutonomousError, ValidationError
from app.agents.software_engineer.autonomous.models import (
    AutonomousRequest,
    AutonomousResponse,
    Workflow,
    QualityReport,
    MemoryEntry,
    Feedback,
)

from app.agents.software_engineer.autonomous.workflow_builder import LocalWorkflowBuilder
from app.agents.software_engineer.autonomous.workflow_executor import LocalWorkflowExecutor
from app.agents.software_engineer.autonomous.task_orchestrator import LocalTaskOrchestrator
from app.agents.software_engineer.autonomous.agent_router import LocalAgentRouter
from app.agents.software_engineer.autonomous.capability_manager import CapabilityManager
from app.agents.software_engineer.autonomous.decision_engine import LocalDecisionEngine
from app.agents.software_engineer.autonomous.context_manager import ContextManager
from app.agents.software_engineer.autonomous.memory_manager import LocalMemoryManager
from app.agents.software_engineer.autonomous.self_validator import LocalSelfValidator
from app.agents.software_engineer.autonomous.recovery_manager import LocalRecoveryManager
from app.agents.software_engineer.autonomous.improvement_engine import LocalImprovementEngine
from app.agents.software_engineer.autonomous.report_generator import ReportGenerator
from app.agents.software_engineer.autonomous.cache import AutonomousCache
from app.agents.software_engineer.autonomous.utils import calculate_checksum

class LocalAutonomousEngine(IAutonomousEngine):
    """The production orchestrator for the Autonomous Software Engineer Integration Engine."""

    def __init__(self, agent: Optional[Any] = None, gateway: Optional[Any] = None, workspace_root: Optional[str] = None) -> None:
        self.agent = agent
        self.gateway = gateway
        self.workspace_root = workspace_root or os.getcwd()

        # Component instances setup
        self.workflow_builder = LocalWorkflowBuilder()
        self.workflow_executor = LocalWorkflowExecutor(agent=self.agent)
        self.task_orchestrator = LocalTaskOrchestrator()
        self.router = LocalAgentRouter()
        self.capabilities = CapabilityManager()
        self.decision_engine = LocalDecisionEngine()
        self.context_mgr = ContextManager(workspace_root=self.workspace_root)
        self.memory_mgr = LocalMemoryManager()
        self.validator = LocalSelfValidator()
        self.recovery_mgr = LocalRecoveryManager()
        self.improvement_engine = LocalImprovementEngine()
        self.report_gen = ReportGenerator()
        self.cache = AutonomousCache(workspace_root=self.workspace_root)

    async def execute_autonomous_workflow(self, request: AutonomousRequest) -> AutonomousResponse:
        """Executes the full 15-stage workflow pipeline."""
        output_dir = os.path.join(self.workspace_root, ".nova", "autonomous")
        os.makedirs(output_dir, exist_ok=True)

        # 1 & 2. Context & Requirements Gathering
        context = self.context_mgr.build_context(request.prompt)

        # 3 & 4. Workflow Generation
        workflow = self.workflow_builder.build_workflow(request, context)

        # 5. Task Ordering
        workflow.steps = self.task_orchestrator.order_tasks(workflow.steps)

        # 6-13. Execution Timeline
        timeline = await self.workflow_executor.execute_workflow(workflow, context)
        success_status = "success" if all(t.success for t in timeline) else "partial"

        # 14. Quality Gates Review
        quality_report = self.validator.validate_gates(context)

        # Commit choices to memory
        self.memory_mgr.commit_memory(MemoryEntry(
            category="decision",
            description=f"Executed workflow '{workflow.id}' for intent: {request.prompt}."
        ))

        # Assemble result
        response = AutonomousResponse(
            status=success_status,
            project_name=context.project_name,
            workflow_executed=workflow,
            execution_timeline=timeline,
            quality_report=quality_report,
            report_markdown=""
        )

        # 15. Report generation
        markdown_report = self.report_gen.generate_markdown(response)
        response.report_markdown = markdown_report

        # Save physical reports
        report_path = os.path.join(output_dir, "project_integration_report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(markdown_report)

        # Update cache
        self.cache.set("last_workflow_id", workflow.id)
        self.cache.set("last_workflow_hash", calculate_checksum(request.prompt))

        return response
