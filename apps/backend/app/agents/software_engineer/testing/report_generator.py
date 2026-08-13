"""Report Generator outputting testing results, coverage reports, and benchmarks.
"""

from app.agents.software_engineer.testing.interfaces import ReportGenerator
from app.agents.software_engineer.testing.models import (
    CoverageReport,
    QualityMetrics,
    TestSuite,
)


class TestingReportGenerator(ReportGenerator):
    """Compiles JSON summaries and Markdown reports."""

    def generate_html_report(
        self, suite: TestSuite, coverage: CoverageReport, metrics: QualityMetrics
    ) -> str:
        """Formats details into HTML blocks.

        Args:
            suite: TestSuite execution metrics.
            coverage: Coverage reports.
            metrics: Maintainability metrics.

        Returns:
            HTML source content string.
        """
        return (
            f"<html>\n"
            f"<head><title>Nova AI - Quality Report</title></head>\n"
            f"<body>\n"
            f"  <h1>Verification Report</h1>\n"
            f"  <p>TestSuite: {suite.suite_name}</p>\n"
            f"  <p>Passed: {suite.passed_count} / Failed: {suite.failed_count}</p>\n"
            f"  <p>Overall Coverage: {coverage.overall_percentage}%</p>\n"
            f"  <p>Maintainability Index: {metrics.maintainability_index}</p>\n"
            f"</body>\n"
            f"</html>"
        )

    def generate_markdown_report(
        self, suite: TestSuite, coverage: CoverageReport, metrics: QualityMetrics
    ) -> str:
        """Formats details into Markdown headers.

        Args:
            suite: TestSuite metrics.
            coverage: Coverage report.
            metrics: Maintainability metrics.

        Returns:
            Markdown content string.
        """
        return (
            f"# Nova AI Quality Verification Report\n\n"
            f"### Test Summary\n"
            f"* **Suite**: {suite.suite_name}\n"
            f"* **Status**: Passed: {suite.passed_count} | Failed: {suite.failed_count}\n\n"
            f"### Coverage & Quality\n"
            f"* **Overall Coverage**: {coverage.overall_percentage}%\n"
            f"* **Maintainability Index**: {metrics.maintainability_index}\n"
        )
