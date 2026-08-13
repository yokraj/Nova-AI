"""Report Generator formats progress, risk, and sprint reports in Markdown and HTML.
"""

from datetime import datetime
from app.agents.software_engineer.project_manager.interfaces import IReportGenerator
from app.agents.software_engineer.project_manager.models import Project, ProjectReport

class LocalReportGenerator(IReportGenerator):
    """Assembles project status details into markdown or HTML strings."""

    def generate_report(self, project: Project, report_type: str, format_type: str) -> ProjectReport:
        """Constructs project metadata reports."""
        epics_md = []
        for epic in project.epics:
            epics_md.append(f"### Epic: {epic.name}")
            epics_md.append(f"Description: {epic.description}")
            for feature in epic.features:
                epics_md.append(f"- **Feature**: {feature.name}")
                for task in feature.tasks:
                    epics_md.append(f"  - [{task.status.value}] {task.title} (Priority: {task.priority}) - {task.estimate.total_hours} hrs")
            epics_md.append("")

        risks_md = []
        for risk in project.risks:
            risks_md.append(f"- **{risk.id}** ({risk.level} Risk): {risk.description} (Mitigation: {risk.mitigation_strategy})")

        milestones_md = []
        for milestone in project.milestones:
            completion_label = "[COMPLETED]" if milestone.is_completed else "[PENDING]"
            milestones_md.append(f"- {completion_label} **{milestone.name}** (Target: {milestone.target_date.strftime('%Y-%m-%d')})")

        content = f"""# Project Management Report: {project.name}
Report Type: {report_type}
Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

## Requirement Summary
- **Goal**: {project.requirements.goal}
- **Technologies**: {', '.join(project.requirements.technology_requirements)}
- **Constraints**: {', '.join(project.requirements.constraints)}

## Project Status & Progress
- **Overall Status**: {project.status.value}
- **Progress**: {project.progress.progress_percentage:.1f}%
- **Completed Tasks**: {project.progress.completed_tasks}/{project.progress.total_tasks}
- **Blocked Tasks**: {project.progress.blocked_tasks}
- **Remaining Work Hours**: {project.progress.remaining_work_hours} hrs
- **ETA**: {project.progress.eta.strftime('%Y-%m-%d %H:%M:%S')}

## Milestone Roadmaps
{chr(10).join(milestones_md)}

## Backlog Hierarchy & Tasks
{chr(10).join(epics_md)}

## Risk Assessment Mitigation Plans
{chr(10).join(risks_md)}
"""
        if format_type.lower() == "html":
            html_content = f"<html><body>{content.replace('# ', '<h1>').replace('## ', '<h2>').replace(chr(10), '<br>')}</body></html>"
            return ProjectReport(
                status="success",
                project_name=project.name,
                report_type=report_type,
                format_type="html",
                content_markdown=html_content
            )

        return ProjectReport(
            status="success",
            project_name=project.name,
            report_type=report_type,
            format_type="markdown",
            content_markdown=content
        )
