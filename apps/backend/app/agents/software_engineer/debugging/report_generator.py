"""Report Generator rendering Markdown summaries and HTML files.
"""

import json
from app.agents.software_engineer.debugging.interfaces import ReportGenerator
from app.agents.software_engineer.debugging.models import DebugReport


class DebugReportFormatter(ReportGenerator):
    """Compiles debug findings outputs."""

    def generate_markdown(self, report: DebugReport) -> str:
        """Formats details as Markdown.

        Args:
            report: Full DebugReport payload.

        Returns:
            Markdown formatted report.
        """
        tb = report.failure.traceback
        cl = report.failure.classification
        rc = report.failure.root_cause

        md_lines = [
            f"# Nova AI Debug & Diagnosis Report",
            f"* **Session ID**: {report.session_id}",
            f"* **Failure Class**: `{cl.category.upper()}`",
            f"* **Exception Name**: `{tb.exception_type}`",
            f"",
            f"### 1. Root Cause Summary",
            f"* **Origin File**: `{rc.origin_file}`",
            f"* **Origin Scope**: `{rc.origin_function}`",
            f"* **Confidence Score**: `{report.confidence.root_cause_confidence * 100.0}%`Hex",
            f"",
            f"### 2. Diagnosis Explanation",
            f"{cl.explanation}",
            f"",
            f"### 3. Traceback Details",
            f"```python",
            f"{tb.raw_text}",
            f"```",
        ]

        if report.repair_plan:
            p = report.repair_plan
            md_lines.extend([
                f"",
                f"### 4. Proposed Repair Plan",
                f"* **Summary**: {p.summary}",
                f"* **Estimated Risk**: `{p.estimated_risk.upper()}`",
                f"* **Success Probability**: `{report.confidence.overall_success_probability * 100.0}%`",
                f"",
                f"#### Suggested Code Patches",
            ])
            for idx, sug in enumerate(p.suggestions, start=1):
                md_lines.extend([
                    f"##### Patch #{idx} - {sug.file_path}",
                    f"```python",
                    f"# Replacement code:",
                    f"{sug.replacement_code}",
                    f"```",
                    f"*Explanation*: {sug.explanation}",
                ])

        return "\n".join(md_lines)

    def generate_html(self, report: DebugReport) -> str:
        """Renders findings details as HTML.

        Args:
            report: DebugReport.

        Returns:
            HTML string content.
        """
        md = self.generate_markdown(report)
        # Simple rendering wrapper
        return (
            f"<html>\n"
            f"<head><title>Debug Report - {report.session_id}</title></head>\n"
            f"<body style='font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 20px;'>\n"
            f"  {md.replace('\n', '<br>')}\n"
            f"</body>\n"
            f"</html>"
        )
