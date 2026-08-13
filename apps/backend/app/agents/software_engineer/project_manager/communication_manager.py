"""Communication Manager drafts updates in Technical, Business, and Executive styles.
"""

from app.agents.software_engineer.project_manager.models import Project

class CommunicationManager:
    """Drafts developer messages or client briefs based on audience roles."""

    def generate_update(self, project: Project, style: str) -> str:
        """Constructs text update matches target style."""
        style_lower = style.lower()
        progress = project.progress
        
        if "technical" in style_lower:
            return f"""[Developer Technical Sync]
Project: {project.name}
Status: {project.status.value} (Progress: {progress.progress_percentage:.1f}%)
Backlog Metrics: {progress.completed_tasks} tasks completed, {progress.pending_tasks} remaining, {progress.blocked_tasks} blocked.
Remaining Effort: {progress.remaining_work_hours} hrs. Estimated Velocity: {progress.velocity} tasks/sprint.
ETA: {progress.eta.strftime('%Y-%m-%d')}
Critical Path Dependency Tasks: {', '.join([alloc.agent_id for alloc in project.resource_allocations])} allocation active.
"""
        elif "executive" in style_lower:
            return f"""[Executive Summary Update]
We are preparing the final delivery for project "{project.name}".
Current completion ratio stands at {progress.progress_percentage:.1f}%. The project is on track with target ETA: {progress.eta.strftime('%Y-%m-%d')}.
Mitigation strategies are deployed for all {len(project.risks)} identified risks.
"""
        else:
            # Business / Default
            return f"""[Business Client Summary Brief]
Dear Stakeholders,
We are pleased to share the progress update for the "{project.name}" system development.
We have completed {progress.completed_tasks} development tasks successfully. The overall progress of features stands at {progress.progress_percentage:.1f}%.
Our target launch date is estimated for {progress.eta.strftime('%Y-%m-%d')}.
"""
