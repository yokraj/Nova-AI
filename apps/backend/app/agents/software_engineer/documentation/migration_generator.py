"""Migration Generator drafting guides describing database schema upgrades or API breaking changes.
"""

from app.agents.software_engineer.documentation.models import MigrationDocument


class MigrationGuideGenerator:
    """Produces database migration scripts guides summaries."""

    def generate_migration_guide(self, target_service: str) -> MigrationDocument:
        """Drafts instructions.

        Args:
            target_service: Name of service or module upgraded.

        Returns:
            MigrationDocument.
        """
        return MigrationDocument(
            target=target_service,
            migration_steps=[
                "1. Run virtual environment dependency sync.",
                "2. Execute database migration alembic upgrades scripts.",
                "3. Verify routing endpoints response status.",
            ],
            breaking_changes=[
                "LocalTestingEngine.execute_testing_pipeline changed signature to async.",
            ],
        )
