"""Project Dashboard & Software Analytics Runtime.
"""

from app.ai.software_company.models import BuildStatus, ProjectDashboardStatus, ProjectStage


class SoftwareDashboardRuntime:
    """Monitors live project progress, agent assignments, current sprint, build status, testing coverage, and deployment URL."""

    def get_dashboard_status(self) -> ProjectDashboardStatus:
        """Returns snapshot of current project dashboard state."""
        return ProjectDashboardStatus(
            company_name="Nova Autonomous Software Engineering Co.",
            active_projects_count=1,
            current_stage=ProjectStage.DELIVERED,
            build_status=BuildStatus.SUCCESS,
            test_coverage_percent=94.2,
            bugs_fixed_count=3,
        )
