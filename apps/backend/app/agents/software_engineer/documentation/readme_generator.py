"""README Generator outputting standard setup guide templates.
"""

from app.agents.software_engineer.documentation.models import ReadmeDocument


class ReadmeGenerator:
    """Produces customized README markdown contents."""

    def generate_readme(self, project_name: str) -> ReadmeDocument:
        """Fills README skeleton.

        Args:
            project_name: Name of project.

        Returns:
            ReadmeDocument.
        """
        return ReadmeDocument(
            overview=f"# {project_name}\n\nTechnical overview of the project and architectural details.",
            installation="## Installation\n\n```bash\nuv sync\n```",
            configuration="## Configuration\n\nConfigure env variables inside `.env` configuration file.",
            usage="## Usage\n\nRun the dev servers:\n```bash\nnpm run dev\n```",
        )
