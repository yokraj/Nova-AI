"""Timeline Generator creates project roadmap timelines and Gantt-style text guides.
"""

from app.agents.software_engineer.project_manager.models import Project

class TimelineGenerator:
    """Renders timelines and milestone targets for roadmap visuals."""

    def generate_timeline_text(self, project: Project) -> str:
        """Returns a text-based Gantt/milestone chart representation."""
        lines = [
            f"# Timeline Roadmap: {project.name}",
            f"Current Project Status: {project.status.value}",
            "==================================================",
            ""
        ]

        for milestone in project.milestones:
            completion_label = "[COMPLETED]" if milestone.is_completed else "[PENDING]"
            target_str = milestone.target_date.strftime('%Y-%m-%d')
            lines.append(f"Phase Target: {target_str} - {completion_label} {milestone.name}")
            for tid in milestone.tasks:
                lines.append(f"  └─ Task: {tid}")
            lines.append("")

        return "\n".join(lines)
