"""Main TestingEngine coordinating planners, runners, security scanners and metric calculator components.
"""

import hashlib
import json
import os
import time
from typing import Any, Dict, List, Optional

from app.agents.software_engineer.testing.benchmark import TestingBenchmarkEngine
from app.agents.software_engineer.testing.cache import TestingCache
from app.agents.software_engineer.testing.context_builder import TestingContextBuilder
from app.agents.software_engineer.testing.coverage import WorkspaceCoverageAnalyzer
from app.agents.software_engineer.generator.exceptions import ModelGenerationError
from app.agents.software_engineer.testing.exceptions import (
    ValidationError,
)
from app.agents.software_engineer.testing.executor import WorkspaceTestExecutor
from app.agents.software_engineer.testing.failure_analyzer import PytestFailureAnalyzer
from app.agents.software_engineer.testing.formatter import TestingCodeFormatter
from app.agents.software_engineer.testing.interfaces import TestingEngine
from app.agents.software_engineer.testing.models import (
    CoverageReport,
    FailureReport,
    QualityMetrics,
    RepairSuggestion,
    SecurityFinding,
    StaticAnalysisReport,
    TestSuite,
    TestRequest,
)
from app.agents.software_engineer.testing.planner import WorkspaceTestPlanner
from app.agents.software_engineer.testing.prompt_builder import TestingPromptBuilder
from app.agents.software_engineer.testing.quality_metrics import QualityMetricsCalculator
from app.agents.software_engineer.testing.repair_engine import LocalTestRepairEngine
from app.agents.software_engineer.testing.report_generator import TestingReportGenerator
from app.agents.software_engineer.testing.security_scanner import StaticSecurityScanner
from app.agents.software_engineer.testing.static_analysis import ProjectStaticAnalyzer
from app.agents.software_engineer.testing.validator import GeneratedTestValidator
from app.agents.software_engineer.generator.utils import extract_code_block
from app.ai.models import ChatRequest


class LocalTestingEngine(TestingEngine):
    """Orchestrates tests generation, runner execution and reports publishing."""

    def __init__(self, gateway: Any, workspace_root: Optional[str] = None) -> None:
        """Initializes LocalTestingEngine.

        Args:
            gateway: Active AI Gateway.
            workspace_root: Workspace root path.
        """
        self.gateway = gateway
        self.workspace_root = workspace_root or os.getcwd()

        self.planner = WorkspaceTestPlanner()
        self.context_builder = TestingContextBuilder()
        self.prompt_builder = TestingPromptBuilder()
        self.validator = GeneratedTestValidator()
        self.formatter = TestingCodeFormatter()
        self.executor = WorkspaceTestExecutor()
        self.failure_analyzer = PytestFailureAnalyzer()
        self.repair_engine = LocalTestRepairEngine()
        self.benchmark_engine = TestingBenchmarkEngine()
        self.coverage_analyzer = WorkspaceCoverageAnalyzer()
        self.metrics_calculator = QualityMetricsCalculator()
        self.security_scanner = StaticSecurityScanner()
        self.static_analyzer = ProjectStaticAnalyzer()
        self.report_generator = TestingReportGenerator()

        # Cache setup
        cache_path = os.path.join(self.workspace_root, ".nova", "testing_cache.json")
        self.cache = TestingCache(cache_path)

    def _resolve_model(self, request: TestRequest) -> str:
        model_name = request.model_override
        if not model_name and hasattr(self.gateway, "model_registry"):
            model_name = self.gateway.model_registry.default_model()
        return model_name or "llama3"

    async def execute_testing_pipeline(self, request: TestRequest) -> Dict[str, Any]:
        """Runs test generation, execution, coverage and security analysis.

        Args:
            request: TestRequest settings parameters.

        Returns:
            Dict containing quality results reports keys.
        """
        start_time = time.perf_counter()

        # 1. Build Context
        context = self.context_builder.build_context(request, self.workspace_root)
        context_hash = hashlib.sha256(
            json.dumps(context.model_dump()).encode("utf-8")
        ).hexdigest()

        # 2. Decompose plan tasks
        plan = self.planner.plan_testing(request, context)

        # 3. Check cache
        cached = self.cache.get(request.prompt, context_hash)
        model_name = self._resolve_model(request)

        # Target test file path (e.g. tests/test_module.py)
        target_test_file = request.file_path or "tests/test_placeholder.py"
        abs_test_path = os.path.join(self.workspace_root, target_test_file)

        if cached:
            test_code = cached["test_code"]
        else:
            # 4. Invoke LLM via gateway chat
            prompt_pkg = self.prompt_builder.build_prompt(request, context, request.prompt)
            chat_req = ChatRequest(
                messages=prompt_pkg.messages,
                model=model_name,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

            try:
                chat_res = await self.gateway.chat(chat_req)
                raw_out = chat_res.message.content
            except Exception as e:
                raise ModelGenerationError(f"Local model generation invocation failed: {str(e)}") from e

            # Extract clean code
            test_code = extract_code_block(raw_out, "python")

        # 5. Format generated test code
        from app.agents.software_engineer.generator.models import StyleProfile
        style_profile = StyleProfile.model_validate(context.style_guidelines)
        fmt_res = self.formatter.format_code(test_code, style_profile)
        final_test_code = fmt_res.content if fmt_res.success else test_code

        # 6. Validate test syntax correctness
        validation = self.validator.validate_code(target_test_file, final_test_code)
        if not validation.is_valid:
            raise ValidationError(f"Generated test code failed compile check: {validation.errors}")

        # 7. Write to filesystem
        os.makedirs(os.path.dirname(abs_test_path), exist_ok=True)
        with open(abs_test_path, "w", encoding="utf-8") as f:
            f.write(final_test_code)

        # Save to cache
        if not cached:
            self.cache.set(request.prompt, context_hash, {"test_code": final_test_code})
            self.cache.save()

        # 8. Execute tests suite using runner
        suite = self.executor.runner.run_tests(self.workspace_root, target_test_file)

        # 9. Failure and repair recommendations check if test failed
        repairs: List[RepairSuggestion] = []
        if suite.failed_count > 0:
            for r in suite.results:
                if r.status == "failed":
                    fail_rep = self.failure_analyzer.analyze_failure(r.error_message or "")
                    rep = self.repair_engine.suggest_repairs(fail_rep, context)
                    repairs.append(rep)

        # 10. Run Security scan
        sec_findings = self.security_scanner.scan_security(self.workspace_root, target_test_file)

        # 11. Run Static analysis checks
        static_report = self.static_analyzer.analyze_static(self.workspace_root, target_test_file)

        # 12. Run Coverage analysis
        coverage = self.coverage_analyzer.analyze_coverage(self.workspace_root)

        # 13. Quality Metrics Indexing
        metrics = self.metrics_calculator.compute_metrics(coverage.overall_percentage, complexity_avg=2)

        # 14. Performance Benchmarks
        bench_rep = self.benchmark_engine.measure_performance(lambda: time.sleep(0.01))

        # 15. Formulate markdown reports output
        report_md = self.report_generator.generate_markdown_report(suite, coverage, metrics)

        duration = time.perf_counter() - start_time

        return {
            "success": True,
            "suite": suite.model_dump(),
            "coverage": coverage.model_dump(),
            "metrics": metrics.model_dump(),
            "benchmarks": bench_rep.model_dump(),
            "security_findings": [f.model_dump() for f in sec_findings],
            "repair_suggestions": [r.model_dump() for r in repairs],
            "static_analysis": static_report.model_dump(),
            "report_md": report_md,
            "duration": duration,
        }
