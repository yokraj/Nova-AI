"""Core DebugEngine implementation coordinating tracebacks parsing, scanners analysis, and repairs generation.
"""

import hashlib
import os
import time
from typing import Any, Dict, List, Optional

from app.agents.software_engineer.debugging.interfaces import DebugEngine
from app.agents.software_engineer.debugging.planner import WorkspaceDebugPlanner
from app.agents.software_engineer.debugging.context_builder import DebugContextBuilder
from app.agents.software_engineer.debugging.stacktrace_parser import PythonStackTraceParser
from app.agents.software_engineer.debugging.failure_classifier import TraceFailureClassifier
from app.agents.software_engineer.debugging.root_cause import TracebackRootCauseAnalyzer
from app.agents.software_engineer.debugging.dependency_checker import ProjectDependencyChecker
from app.agents.software_engineer.debugging.import_validator import ASTImportValidator
from app.agents.software_engineer.debugging.runtime_analyzer import LocalRuntimeAnalyzer
from app.agents.software_engineer.debugging.memory_analyzer import StaticMemoryAnalyzer
from app.agents.software_engineer.debugging.performance_analyzer import StaticPerformanceAnalyzer
from app.agents.software_engineer.debugging.repair_generator import LocalRepairGenerator
from app.agents.software_engineer.debugging.repair_validator import WorkspaceRepairValidator
from app.agents.software_engineer.debugging.confidence_estimator import DiagnosticConfidenceEstimator
from app.agents.software_engineer.debugging.bug_database import LocalBugDatabase
from app.agents.software_engineer.debugging.knowledge_base import LocalKnowledgeBase
from app.agents.software_engineer.debugging.report_generator import DebugReportFormatter
from app.agents.software_engineer.debugging.cache import DebuggingCache
from app.agents.software_engineer.debugging.models import (
    ConfidenceReport,
    DebugContext,
    DebugReport,
    DebugRequest,
    DebugSession,
    Failure,
    RepairPlan,
    RepairValidation,
    RootCause,
    StackTrace,
)


class LocalDebuggingEngine(DebugEngine):
    """Main orchestrator running the debugging pipeline."""

    def __init__(self, gateway: Any, workspace_root: Optional[str] = None) -> None:
        """Initializes LocalDebuggingEngine.

        Args:
            gateway: Active AI Gateway.
            workspace_root: Workspace root path.
        """
        self.gateway = gateway
        self.workspace_root = workspace_root or os.getcwd()

        self.planner = WorkspaceDebugPlanner()
        self.context_builder = DebugContextBuilder()
        self.stacktrace_parser = PythonStackTraceParser()
        self.failure_classifier = TraceFailureClassifier()
        self.root_cause_analyzer = TracebackRootCauseAnalyzer()
        self.dependency_checker = ProjectDependencyChecker()
        self.import_validator = ASTImportValidator()
        self.runtime_analyzer = LocalRuntimeAnalyzer()
        self.memory_analyzer = StaticMemoryAnalyzer()
        self.performance_analyzer = StaticPerformanceAnalyzer()
        self.repair_generator = LocalRepairGenerator(self.gateway)
        self.repair_validator = WorkspaceRepairValidator()
        self.confidence_estimator = DiagnosticConfidenceEstimator()
        self.report_generator = DebugReportFormatter()

        # Offline local files setup
        nova_dir = os.path.join(self.workspace_root, ".nova")
        self.bug_db = LocalBugDatabase(os.path.join(nova_dir, "bug_database.json"))
        self.knowledge_base = LocalKnowledgeBase(os.path.join(nova_dir, "knowledge_base.json"))
        self.cache = DebuggingCache(os.path.join(nova_dir, "debugging_cache.json"))

    def _get_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    async def run_diagnose(self, request: DebugRequest) -> DebugReport:
        """Parses logs stack traces, identifies root causes, and estimates repairs.

        Args:
            request: DebugRequest settings parameters.

        Returns:
            DebugReport.
        """
        tb_hash = self._get_hash(request.traceback_str)

        # 1. Check cache
        cached = self.cache.get(tb_hash)
        if cached:
            try:
                return DebugReport.model_validate(cached)
            except Exception:
                pass

        # 2. Compile context
        context = self.context_builder.build_context(request, self.workspace_root)

        # 3. Traceback Parser
        traceback = self.stacktrace_parser.parse_traceback(request.traceback_str)

        # 4. Failure Classifier
        classification = self.failure_classifier.classify_failure(traceback)

        # 5. Root Cause Detector
        root_cause = self.root_cause_analyzer.detect_root_cause(traceback, context)

        # 6. Audits check run (Dependencies, Imports, Memory, Performance)
        dep_issues = self.dependency_checker.check_dependencies(self.workspace_root)
        
        target_file = root_cause.origin_file
        import_issues = []
        mem_issues = []
        perf_issues = []
        if target_file and target_file != "unknown":
            import_issues = self.import_validator.validate_imports(self.workspace_root, target_file)
            mem_issues = self.memory_analyzer.analyze_memory(self.workspace_root, target_file)
            perf_issues = self.performance_analyzer.analyze_performance(self.workspace_root, target_file)

        # 7. Check Bug Database for existing resolves
        plan = self.bug_db.get_known_fix(traceback.exception_type, traceback.exception_message)

        # 8. Generation if no previous resolutions cached
        if not plan:
            plan = await self.repair_generator.generate_repair(request, context, root_cause)

        # 9. Verify proposed patch compiles cleanly
        validation = self.repair_validator.validate_repair(plan)

        # 10. Estimate confidence indices
        confidence = self.confidence_estimator.estimate_confidence(root_cause, plan)

        # 11. Compile output report schemas
        dummy_session = f"session-{tb_hash[:8]}"
        failure_model = Failure(
            traceback=traceback,
            classification=classification,
            root_cause=root_cause,
        )

        dummy_report = DebugReport(
            session_id=dummy_session,
            failure=failure_model,
            repair_plan=plan,
            validation=validation,
            confidence=confidence,
            markdown_report="",
        )

        md_content = self.report_generator.generate_markdown(dummy_report)
        # Update field in the instance
        dummy_report = DebugReport(
            session_id=dummy_session,
            failure=failure_model,
            repair_plan=plan,
            validation=validation,
            confidence=confidence,
            markdown_report=md_content,
        )

        # Index in Bug Database if fix is valid and high confidence
        if validation.is_valid and confidence.overall_success_probability >= 0.7:
            self.bug_db.record_resolution(traceback.exception_type, traceback.exception_message, plan)

        # Index in Local Knowledge Base
        self.knowledge_base.index_report(dummy_report)

        # Cache results
        self.cache.set(tb_hash, dummy_report.model_dump())

        return dummy_report
