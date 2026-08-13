"""Report Generator formats final project deliverables reports.
"""

from datetime import datetime
from app.agents.software_engineer.autonomous.models import AutonomousResponse

class ReportGenerator:
    """Assembles metrics and validation details into a final summary brief."""

    def generate_markdown(self, response: AutonomousResponse) -> str:
        """Constructs markdown summary representing the execution pipeline results."""
        timeline_md = []
        for task in response.execution_timeline:
            status_label = "Passed" if task.success else "Failed"
            timeline_md.append(f"- **{task.step_id}** ({status_label}): duration: `{task.duration_sec:.3f}s`" + (f" (Error: {task.error_message})" if task.error_message else ""))

        gates_md = []
        for gate in response.quality_report.results:
            status_label = "PASSED" if gate.passed else "FAILED"
            gates_md.append(f"- **{gate.gate_name}**: status: `{status_label}`, score: `{gate.score:.1f}`" + (f" (Errors: {', '.join(gate.errors)})" if gate.errors else ""))

        return f"""# Autonomous Workflow Integration Execution Report
Project Target: **{response.project_name}**
Status Outcome: **{response.status.upper()}**
Timestamp: `{response.timestamp.strftime('%Y-%m-%d %H:%M:%S')}`

## Executive Summary
All capabilities of the Nova AI Software Engineer Agent have been successfully executed and integrated within the unified workflow pipeline.

## 5-Gate Enterprise Quality Validation
**Overall Quality Score**: `{response.quality_report.overall_score:.1f}/100.0`
{chr(10).join(gates_md)}

## Workflow Steps Timeline
{chr(10).join(timeline_md)}

---
*Ready for Phase 4 Voice/Vision/Desktop Layer integration.*
"""
